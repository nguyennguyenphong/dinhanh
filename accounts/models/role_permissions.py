# ============================================================================
# FILE: apps/accounts/models.py
# Role-Permission Relationship Models
# ============================================================================

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class RolePermission(models.Model):
    """
    Through model for Role-Permission many-to-many relationship

    This model represents the assignment of permissions to roles.
    It allows for:
    - Assigning multiple permissions to a role
    - Tracking when permissions were assigned and by whom
    - Soft delete support via is_active flag
    - Audit trail of permission changes
    - Batch operations for efficiency

    Design Pattern:
    - Uses explicit through model instead of implicit M2M
    - Allows additional metadata (assigned_at, assigned_by_id)
    - Enables soft delete without losing audit history
    - Supports cascading deletes for data integrity

    Example:
        # Assign permission to role
        role_perm = RolePermission.objects.create(
            role=role,
            permission=permission,
            assigned_by_id=admin_user.id
        )

        # Get all active permissions for a role
        permissions = RolePermission.objects.filter(
            role=role,
            is_active=True
        ).select_related('permission')

        # Revoke permission from role (soft delete)
        role_perm.revoke()
    """

    id = models.AutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    role = models.ForeignKey(
        "Role",
        on_delete=models.CASCADE,
        related_name="role_permissions",
        db_index=True,
        help_text="Role that has this permission",
    )
    permission = models.ForeignKey(
        "Permission",
        on_delete=models.CASCADE,
        related_name="role_permissions",
        db_index=True,
        help_text="Permission assigned to the role",
    )

    # ========================================================================
    # STATUS AND TRACKING
    # ========================================================================

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Permission assignment is active (soft delete via flag)",
    )

    # ========================================================================
    # AUDIT INFORMATION
    # ========================================================================

    assigned_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When this permission was assigned to the role",
    )
    assigned_by_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="User ID who assigned this permission (admin user)",
    )
    assigned_by_username = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        help_text="Username of who assigned this permission (snapshot)",
    )

    # Revocation tracking
    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this permission was revoked from the role",
    )
    revoked_by_id = models.IntegerField(
        null=True, blank=True, help_text="User ID who revoked this permission"
    )
    revoked_by_username = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        help_text="Username of who revoked this permission (snapshot)",
    )

    # Additional metadata
    reason = models.TextField(
        blank=True,
        null=True,
        help_text="Reason for assigning or revoking this permission",
    )

    class Meta:
        db_table = "role_permissions"
        verbose_name = _("Role Permission")
        verbose_name_plural = _("Role Permissions")
        ordering = ["role", "permission"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Primary key constraint: role_id + permission_id
            models.UniqueConstraint(
                fields=["role", "permission"],
                name="unique_role_permission",
                violation_error_message="This permission is already assigned to this role",
            ),
        ]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Index for finding active permissions for a role
            models.Index(
                fields=["role", "is_active"], name="idx_role_perm_role_active"
            ),
            # Index for finding roles with a specific permission
            models.Index(
                fields=["permission", "is_active"],
                name="idx_role_perm_perm_active",
            ),
            # Index for audit trail
            models.Index(
                fields=["assigned_at"], name="idx_role_perm_assigned_at"
            ),
            # Composite index for common queries
            models.Index(
                fields=["role", "permission", "is_active"],
                name="idx_role_permission_composite",
            ),
        ]

    def __str__(self):
        """String representation"""
        status = "active" if self.is_active else "revoked"
        return f"{self.role.slug} -> {self.permission.codename} ({status})"

    def clean(self):
        """
        Validate role-permission relationship

        Rules:
        - Role and permission must belong to same tenant
        - Cannot assign same permission twice to same role
        """
        # Check tenant consistency
        if self.role.tenant_id != self.permission.tenant_id:
            raise ValidationError("Role and permission must belong to the same tenant")

        # Check for duplicates (excluding self)
        duplicate = (
            RolePermission.objects.filter(role=self.role, permission=self.permission)
            .exclude(pk=self.pk)
            .exists()
        )

        if duplicate:
            raise ValidationError("This permission is already assigned to this role")

    def save(self, *args, **kwargs):
        """
        Override save to enforce business rules
        """
        self.clean()
        super().save(*args, **kwargs)

    def revoke(self, revoked_by_id=None, revoked_by_username=None, reason=None):
        """
        Revoke this permission from the role (soft delete)

        Args:
            revoked_by_id: User ID who is revoking
            revoked_by_username: Username who is revoking
            reason: Reason for revocation

        Example:
            role_perm.revoke(
                revoked_by_id=admin.id,
                revoked_by_username=admin.username,
                reason='User no longer needs this permission'
            )
        """
        self.is_active = False
        self.revoked_at = timezone.now()
        self.revoked_by_id = revoked_by_id
        self.revoked_by_username = revoked_by_username
        self.reason = reason
        self.save(
            update_fields=[
                "is_active",
                "revoked_at",
                "revoked_by_id",
                "revoked_by_username",
                "reason",
            ]
        )

    def restore(self):
        """
        Restore a revoked permission (reactivate)

        Example:
            role_perm.restore()
        """
        self.is_active = True
        self.revoked_at = None
        self.revoked_by_id = None
        self.revoked_by_username = None
        self.save(
            update_fields=[
                "is_active",
                "revoked_at",
                "revoked_by_id",
                "revoked_by_username",
            ]
        )

    @classmethod
    def assign_permission(
        cls, role, permission, assigned_by_id=None, assigned_by_username=None
    ):
        """
        Assign a permission to a role

        Args:
            role: Role instance
            permission: Permission instance
            assigned_by_id: User ID who is assigning
            assigned_by_username: Username who is assigning

        Returns:
            Tuple (RolePermission instance, created boolean)

        Example:
            role_perm, created = RolePermission.assign_permission(
                role=role,
                permission=permission,
                assigned_by_id=admin.id,
                assigned_by_username=admin.username
            )
        """
        role_perm, created = cls.objects.get_or_create(
            role=role,
            permission=permission,
            defaults={
                "is_active": True,
                "assigned_by_id": assigned_by_id,
                "assigned_by_username": assigned_by_username,
            },
        )

        # If it was revoked before, restore it
        if not created and not role_perm.is_active:
            role_perm.restore()

        return role_perm, created

    @classmethod
    def assign_permissions_batch(
        cls, role, permissions, assigned_by_id=None, assigned_by_username=None
    ):
        """
        Assign multiple permissions to a role in batch

        Args:
            role: Role instance
            permissions: List of Permission instances
            assigned_by_id: User ID who is assigning
            assigned_by_username: Username who is assigning

        Returns:
            List of created RolePermission instances

        Example:
            perms = Permission.objects.filter(module='tickets')
            created = RolePermission.assign_permissions_batch(
                role=role,
                permissions=perms,
                assigned_by_id=admin.id
            )
        """
        role_perms = []
        for permission in permissions:
            role_perm, _ = cls.assign_permission(
                role=role,
                permission=permission,
                assigned_by_id=assigned_by_id,
                assigned_by_username=assigned_by_username,
            )
            role_perms.append(role_perm)
        return role_perms

    @classmethod
    def revoke_permission(
        cls, role, permission, revoked_by_id=None, revoked_by_username=None, reason=None
    ):
        """
        Revoke a permission from a role

        Args:
            role: Role instance
            permission: Permission instance
            revoked_by_id: User ID who is revoking
            revoked_by_username: Username who is revoking
            reason: Reason for revocation

        Returns:
            RolePermission instance or None

        Example:
            RolePermission.revoke_permission(
                role=role,
                permission=permission,
                revoked_by_id=admin.id,
                reason='Permission no longer needed'
            )
        """
        try:
            role_perm = cls.objects.get(role=role, permission=permission)
            role_perm.revoke(
                revoked_by_id=revoked_by_id,
                revoked_by_username=revoked_by_username,
                reason=reason,
            )
            return role_perm
        except cls.DoesNotExist:
            return None

    @classmethod
    def revoke_permissions_batch(
        cls,
        role,
        permissions,
        revoked_by_id=None,
        revoked_by_username=None,
        reason=None,
    ):
        """
        Revoke multiple permissions from a role in batch

        Args:
            role: Role instance
            permissions: List of Permission instances
            revoked_by_id: User ID who is revoking
            revoked_by_username: Username who is revoking
            reason: Reason for revocation

        Returns:
            List of revoked RolePermission instances

        Example:
            perms = Permission.objects.filter(module='sensitive')
            revoked = RolePermission.revoke_permissions_batch(
                role=role,
                permissions=perms,
                revoked_by_id=admin.id,
                reason='Security policy update'
            )
        """
        revoked = []
        for permission in permissions:
            role_perm = cls.revoke_permission(
                role=role,
                permission=permission,
                revoked_by_id=revoked_by_id,
                revoked_by_username=revoked_by_username,
                reason=reason,
            )
            if role_perm:
                revoked.append(role_perm)
        return revoked

    @classmethod
    def get_active_permissions_for_role(cls, role):
        """
        Get all active permissions for a role

        Args:
            role: Role instance

        Returns:
            QuerySet of Permission objects

        Example:
            permissions = RolePermission.get_active_permissions_for_role(role)
        """
        return (
            cls.objects.filter(role=role, is_active=True)
            .select_related("permission")
            .values_list("permission", flat=True)
        )

    @classmethod
    def get_active_permission_codes_for_role(cls, role):
        """
        Get list of active permission codes for a role

        Args:
            role: Role instance

        Returns:
            List of permission codenames

        Example:
            codes = RolePermission.get_active_permission_codes_for_role(role)
            # Returns: ['tickets.view_ticket', 'tickets.add_ticket', ...]
        """
        from accounts.models.permissions import Permission

        return list(
            Permission.objects.filter(
                role_permissions__role=role, role_permissions__is_active=True
            )
            .values_list("codename", flat=True)
            .distinct()
        )

    @classmethod
    def get_roles_with_permission(cls, permission):
        """
        Get all roles that have a specific permission

        Args:
            permission: Permission instance

        Returns:
            QuerySet of Role objects

        Example:
            roles = RolePermission.get_roles_with_permission(permission)
        """
        from accounts.models.roles import Role

        return Role.objects.filter(
            role_permissions__permission=permission, role_permissions__is_active=True
        ).distinct()

    @classmethod
    def get_permission_stats(cls, role):
        """
        Get statistics about permissions for a role

        Args:
            role: Role instance

        Returns:
            Dictionary with stats

        Example:
            stats = RolePermission.get_permission_stats(role)
            # Returns: {
            #     'total': 15,
            #     'active': 12,
            #     'revoked': 3,
            #     'by_module': {'tickets': 5, 'vehicles': 7, ...}
            # }
        """
        from accounts.models.permissions import Permission

        role_perms = cls.objects.filter(role=role)

        # Count by module
        by_module = {}
        for module in (
            Permission.objects.filter(
                role_permissions__role=role, role_permissions__is_active=True
            )
            .values_list("module", flat=True)
            .distinct()
        ):
            count = Permission.objects.filter(
                module=module,
                role_permissions__role=role,
                role_permissions__is_active=True,
            ).count()
            by_module[module] = count

        return {
            "total": role_perms.count(),
            "active": role_perms.filter(is_active=True).count(),
            "revoked": role_perms.filter(is_active=False).count(),
            "by_module": by_module,
        }
