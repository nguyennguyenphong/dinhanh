# ============================================================================
# FILE: apps/accounts/models.py
# User-Role Relationship Models with Audit Trail
# ============================================================================

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from safedelete.models import SOFT_DELETE_CASCADE, SafeDeleteModel

from core.models import BaseModel


class UserRole(BaseModel):
    """
    Through model for User-Role many-to-many relationship

    This model represents the assignment of roles to users.
    It allows for:
    - Assigning multiple roles to a user
    - Tracking who granted the role and when
    - Audit trail of role assignments
    - Soft delete support via is_active flag
    - Batch operations for efficiency

    Design Pattern:
    - Uses explicit through model instead of implicit M2M
    - Allows additional metadata (granted_by, granted_at)
    - Enables audit trail without losing history
    - Supports cascading deletes for data integrity

    Features:
    - Multi-tenant support: Users and roles are tenant-specific
    - Audit trail: Track who granted roles and when
    - Soft delete: Can revoke roles without deleting history
    - Validation: Ensure user and role belong to same tenant
    - Permissions inheritance: User gets all role permissions

    Example:
        # Assign role to user
        user_role = UserRole.objects.create(
            user=user,
            role=role,
            granted_by=admin_user
        )

        # Get all active roles for a user
        roles = UserRole.objects.filter(
            user=user,
            is_active=True
        ).select_related('role')

        # Revoke role from user (soft delete)
        user_role.revoke()

        # Get all users with specific role
        users = UserRole.get_users_with_role(role)
    """

    id = models.AutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    user = models.ForeignKey(
        "UserAccount",
        on_delete=models.CASCADE,
        related_name="user_roles",
        db_index=True,
        help_text="User assigned to this role",
    )
    role = models.ForeignKey(
        "Role",
        on_delete=models.CASCADE,
        related_name="user_roles",
        db_index=True,
        help_text="Role assigned to the user",
    )

    # ========================================================================
    # STATUS AND TRACKING
    # ========================================================================

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Role assignment is active (soft delete via flag)",
    )

    # ========================================================================
    # AUDIT INFORMATION
    # ========================================================================

    granted_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When this role was granted to the user",
    )
    granted_by = models.ForeignKey(
        "UserAccount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="granted_roles",
        help_text="User who granted this role (admin/manager)",
    )
    granted_by_username = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        help_text="Username of who granted this role (snapshot)",
    )

    # Revocation tracking
    revoked_at = models.DateTimeField(
        null=True, blank=True, help_text="When this role was revoked from the user"
    )
    revoked_by = models.ForeignKey(
        "UserAccount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="revoked_roles",
        help_text="User who revoked this role",
    )
    revoked_by_username = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        help_text="Username of who revoked this role (snapshot)",
    )

    # Additional metadata
    reason = models.TextField(
        blank=True, null=True, help_text="Reason for granting or revoking this role"
    )

    # Expiration support
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Role assignment expires at this time (null = never)",
    )

    class Meta:
        db_table = "user_roles"
        verbose_name = _("User Role")
        verbose_name_plural = _("User Roles")
        ordering = ["user", "role"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Primary key constraint: user_id + role_id
            models.UniqueConstraint(
                fields=["user", "role"],
                name="unique_user_role",
                violation_error_message="This role is already assigned to this user",
            ),
        ]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Index for finding active roles for a user
            models.Index(
                fields=["user", "is_active"], name="idx_user_role_user_active"
            ),
            # Index for finding users with a specific role
            models.Index(
                fields=["role", "is_active"], name="idx_user_role_role_active"
            ),
            # Index for audit trail
            models.Index(fields=["granted_at"], name="idx_user_role_granted_at"),
            # Index for expired roles
            models.Index(fields=["expires_at"], name="idx_user_role_expires_at"),
            # Composite index for common queries
            models.Index(
                fields=["user", "role", "is_active"], name="idx_user_role_composite"
            ),
        ]

    def __str__(self):
        """String representation"""
        status = "active" if self.is_active else "revoked"
        return f"{self.user.username} -> {self.role.slug} ({status})"

    def clean(self):
        """
        Validate user-role relationship

        Rules:
        - User and role must belong to same tenant
        - Cannot assign same role twice to same user
        - Granted_by user must belong to same tenant
        """
        # Check tenant consistency
        if self.user.tenant_id != self.role.tenant_id:
            raise ValidationError("User and role must belong to the same tenant")

        # Check granted_by tenant consistency
        if self.granted_by and self.granted_by.tenant_id != self.user.tenant_id:
            raise ValidationError("Granted by user must belong to the same tenant")

        # Check for duplicates (excluding self)
        duplicate = (
            UserRole.objects.filter(user=self.user, role=self.role)
            .exclude(pk=self.pk)
            .exists()
        )

        if duplicate:
            raise ValidationError("This role is already assigned to this user")

    def save(self, *args, **kwargs):
        """
        Override save to enforce business rules
        """
        self.clean()
        super().save(*args, **kwargs)

    def is_expired(self):
        """
        Check if role assignment has expired

        Returns:
            Boolean
        """
        if not self.expires_at:
            return False

        return timezone.now() > self.expires_at

    def revoke(self, revoked_by=None, revoked_by_username=None, reason=None):
        """
        Revoke this role from the user (soft delete)

        Args:
            revoked_by: UserAccount instance who is revoking
            revoked_by_username: Username who is revoking
            reason: Reason for revocation

        Example:
            user_role.revoke(
                revoked_by=admin_user,
                revoked_by_username=admin_user.username,
                reason='User no longer needs this role'
            )
        """
        self.is_active = False
        self.revoked_at = timezone.now()
        self.revoked_by = revoked_by
        self.revoked_by_username = revoked_by_username
        self.reason = reason
        self.save(
            update_fields=[
                "is_active",
                "revoked_at",
                "revoked_by",
                "revoked_by_username",
                "reason",
            ]
        )

    def restore(self):
        """
        Restore a revoked role (reactivate)

        Example:
            user_role.restore()
        """
        self.is_active = True
        self.revoked_at = None
        self.revoked_by = None
        self.revoked_by_username = None
        self.save(
            update_fields=[
                "is_active",
                "revoked_at",
                "revoked_by",
                "revoked_by_username",
            ]
        )

    @classmethod
    def assign_role(
        cls,
        user,
        role,
        granted_by=None,
        granted_by_username=None,
        reason=None,
        expires_at=None,
    ):
        """
        Assign a role to a user

        Args:
            user: UserAccount instance
            role: Role instance
            granted_by: UserAccount instance who is granting
            granted_by_username: Username who is granting
            reason: Reason for assignment
            expires_at: When role expires (optional)

        Returns:
            Tuple (UserRole instance, created boolean)

        Example:
            user_role, created = UserRole.assign_role(
                user=user,
                role=role,
                granted_by=admin_user,
                granted_by_username=admin_user.username,
                reason='Promoted to manager',
                expires_at=timezone.now() + timedelta(days=90)
            )
        """
        user_role, created = cls.objects.get_or_create(
            user=user,
            role=role,
            defaults={
                "is_active": True,
                "granted_by": granted_by,
                "granted_by_username": granted_by_username,
                "reason": reason,
                "expires_at": expires_at,
            },
        )

        # If it was revoked before, restore it
        if not created and not user_role.is_active:
            user_role.restore()

        return user_role, created

    @classmethod
    def assign_roles_batch(
        cls, user, roles, granted_by=None, granted_by_username=None, reason=None
    ):
        """
        Assign multiple roles to a user in batch

        Args:
            user: UserAccount instance
            roles: List of Role instances
            granted_by: UserAccount instance who is granting
            granted_by_username: Username who is granting
            reason: Reason for assignment

        Returns:
            List of created UserRole instances

        Example:
            roles = Role.objects.filter(is_system=False)
            created = UserRole.assign_roles_batch(
                user=user,
                roles=roles,
                granted_by=admin_user,
                reason='Bulk role assignment'
            )
        """
        user_roles = []
        for role in roles:
            user_role, _ = cls.assign_role(
                user=user,
                role=role,
                granted_by=granted_by,
                granted_by_username=granted_by_username,
                reason=reason,
            )
            user_roles.append(user_role)
        return user_roles

    @classmethod
    def revoke_role(
        cls, user, role, revoked_by=None, revoked_by_username=None, reason=None
    ):
        """
        Revoke a role from a user

        Args:
            user: UserAccount instance
            role: Role instance
            revoked_by: UserAccount instance who is revoking
            revoked_by_username: Username who is revoking
            reason: Reason for revocation

        Returns:
            UserRole instance or None

        Example:
            UserRole.revoke_role(
                user=user,
                role=role,
                revoked_by=admin_user,
                reason='Demoted from manager'
            )
        """
        try:
            user_role = cls.objects.get(user=user, role=role)
            user_role.revoke(
                revoked_by=revoked_by,
                revoked_by_username=revoked_by_username,
                reason=reason,
            )
            return user_role
        except cls.DoesNotExist:
            return None

    @classmethod
    def revoke_roles_batch(
        cls, user, roles, revoked_by=None, revoked_by_username=None, reason=None
    ):
        """
        Revoke multiple roles from a user in batch

        Args:
            user: UserAccount instance
            roles: List of Role instances
            revoked_by: UserAccount instance who is revoking
            revoked_by_username: Username who is revoking
            reason: Reason for revocation

        Returns:
            List of revoked UserRole instances

        Example:
            roles = user.get_roles()
            revoked = UserRole.revoke_roles_batch(
                user=user,
                roles=roles,
                revoked_by=admin_user,
                reason='User terminated'
            )
        """
        revoked = []
        for role in roles:
            user_role = cls.revoke_role(
                user=user,
                role=role,
                revoked_by=revoked_by,
                revoked_by_username=revoked_by_username,
                reason=reason,
            )
            if user_role:
                revoked.append(user_role)
        return revoked

    @classmethod
    def get_active_roles_for_user(cls, user):
        """
        Get all active roles for a user

        Args:
            user: UserAccount instance

        Returns:
            QuerySet of Role objects

        Example:
            roles = UserRole.get_active_roles_for_user(user)
        """
        from accounts.models.roles import Role

        return (
            Role.objects.filter(user_roles__user=user, user_roles__is_active=True)
            .filter(
                Q(user_roles__expires_at__isnull=True)
                | Q(user_roles__expires_at__gt=timezone.now())
            )
            .distinct()
        )

    @classmethod
    def get_active_role_codes_for_user(cls, user):
        """
        Get list of active role codes for a user

        Args:
            user: UserAccount instance

        Returns:
            List of role slugs

        Example:
            codes = UserRole.get_active_role_codes_for_user(user)
            # Returns: ['super-admin', 'manager', ...]
        """
        return list(cls.get_active_roles_for_user(user).values_list("slug", flat=True))

    @classmethod
    def get_users_with_role(cls, role):
        """
        Get all users that have a specific role

        Args:
            role: Role instance

        Returns:
            QuerySet of UserAccount objects

        Example:
            users = UserRole.get_users_with_role(role)
        """
        from accounts.models.user_accounts import UserAccount

        return (
            UserAccount.objects.filter(
                user_roles__role=role, user_roles__is_active=True
            )
            .filter(
                Q(user_roles__expires_at__isnull=True)
                | Q(user_roles__expires_at__gt=timezone.now())
            )
            .distinct()
        )

    @classmethod
    def get_role_stats(cls, user):
        """
        Get statistics about roles for a user

        Args:
            user: UserAccount instance

        Returns:
            Dictionary with stats

        Example:
            stats = UserRole.get_role_stats(user)
            # Returns: {
            #     'total': 3,
            #     'active': 2,
            #     'expired': 1,
            #     'by_module': {'tickets': 5, 'vehicles': 3, ...}
            # }
        """
        from accounts.models.permissions import Permission

        user_roles = cls.objects.filter(user=user)

        # Count permissions by module
        by_module = {}
        for module in (
            Permission.objects.filter(
                role_permissions__role__user_roles__user=user,
                role_permissions__is_active=True,
            )
            .values_list("module", flat=True)
            .distinct()
        ):
            count = Permission.objects.filter(
                module=module,
                role_permissions__role__user_roles__user=user,
                role_permissions__is_active=True,
            ).count()
            by_module[module] = count

        return {
            "total": user_roles.count(),
            "active": user_roles.filter(is_active=True).count(),
            "expired": user_roles.filter(is_active=False).count(),
            "by_module": by_module,
        }
