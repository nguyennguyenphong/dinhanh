# ============================================================================
# FILE: apps/branches/models.py
# Branch Models with Multi-Tenant Support
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator, RegexValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from pytz import common_timezones
from tenants.models.tenants import Tenant


class Branch(models.Model):
    """
    Branch model for multi-tenant organization structure

    Features:
    - Multi-tenant support: Each tenant can have multiple branches
    - Hierarchical structure: Support for parent-child branches
    - Timezone management: Each branch has its own timezone
    - Manager assignment: Track branch manager
    - Metadata storage: Flexible JSON storage for branch-specific settings
    - Contact information: Phone, email, address
    - Status tracking: Active/inactive branches
    - Audit trail: Track creation and updates

    Use Cases:
    - Regional offices/branches
    - Depot locations
    - Service centers
    - Warehouse locations
    - Franchise locations

    Example:
        branch = Branch.objects.create(
            tenant=tenant,
            code='HCM',
            name='Ho Chi Minh City Branch',
            address='123 Nguyen Hue, District 1, HCMC',
            phone='+84283334444',
            email='hcm@example.com',
            manager=manager_user,
            timezone='Asia/Ho_Chi_Minh',
            metadata={
                'region': 'South',
                'capacity': 500,
                'established_year': 2020
            }
        )
    """

    # Timezone choices
    TIMEZONE_CHOICES = [(tz, tz) for tz in common_timezones]

    id = models.AutoField(primary_key=True)

    # ========================================================================
    # MULTI-TENANT RELATIONSHIP
    # ========================================================================

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="branches",
        db_index=True,
        help_text="Tenant that owns this branch",
    )

    # ========================================================================
    # BRANCH IDENTIFICATION
    # ========================================================================

    code = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r"^[A-Z0-9_]+$",
                message="Code must contain only uppercase letters, numbers, and underscores",
            )
        ],
        help_text='Unique code for the branch (e.g., "HCM", "HN", "DN")',
    )
    name = models.CharField(max_length=255, help_text="Display name of the branch")

    # ========================================================================
    # CONTACT INFORMATION
    # ========================================================================

    address = models.TextField(
        blank=True, null=True, help_text="Physical address of the branch"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$", message="Invalid phone number format"
            )
        ],
        help_text="Contact phone number",
    )
    email = models.EmailField(
        max_length=254,
        blank=True,
        null=True,
        validators=[EmailValidator()],
        help_text="Contact email address",
    )

    # ========================================================================
    # MANAGEMENT
    # ========================================================================

    manager = models.ForeignKey(
        "accounts.UserAccount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_branches",
        help_text="Manager of this branch",
    )

    # ========================================================================
    # LOCATION & TIMEZONE
    # ========================================================================

    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="Latitude coordinate",
    )
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="Longitude coordinate",
    )
    timezone = models.CharField(
        max_length=50,
        choices=TIMEZONE_CHOICES,
        default="Asia/Ho_Chi_Minh",
        help_text="Timezone for this branch",
    )

    # ========================================================================
    # STATUS
    # ========================================================================

    is_active = models.BooleanField(
        default=True, db_index=True, help_text="Branch is active and operational"
    )

    # ========================================================================
    # METADATA
    # ========================================================================

    metadata = models.JSONField(
        default=dict, blank=True, help_text="Branch-specific metadata and settings"
    )

    # ========================================================================
    # TIMESTAMPS
    # ========================================================================

    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, help_text="When this branch was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="When this branch was last updated"
    )

    class Meta:
        db_table = "branches"
        verbose_name = _("Branch")
        verbose_name_plural = _("Branches")
        ordering = ["code"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Unique code per tenant
            models.UniqueConstraint(
                fields=["tenant", "code"],
                name="unique_tenant_branch_code",
                violation_error_message="Branch code must be unique within tenant",
            ),
        ]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Index for finding active branches
            models.Index(
                fields=["tenant", "is_active"], name="idx_branch_tenant_active"
            ),
            # Index for manager queries
            models.Index(fields=["manager_id"], name="idx_branch_manager"),
            # Index for timezone queries
            models.Index(fields=["timezone"], name="idx_branch_timezone"),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.code} - {self.name} ({self.tenant.code})"

    def save(self, *args, **kwargs):
        """
        Override save to enforce business rules
        """
        # Validate manager belongs to same tenant
        if self.manager and self.manager.tenant_id != self.tenant_id:
            raise ValidationError("Manager must belong to the same tenant")

        # Validate timezone
        if self.timezone not in dict(self.TIMEZONE_CHOICES):
            raise ValidationError(f"Invalid timezone: {self.timezone}")

        super().save(*args, **kwargs)

    def get_local_time(self):
        """
        Get current time in branch timezone

        Returns:
            datetime object in branch timezone

        Example:
            local_time = branch.get_local_time()
        """
        import pytz

        tz = pytz.timezone(self.timezone)
        return timezone.now().astimezone(tz)

    def get_metadata(self, key, default=None):
        """
        Get metadata value

        Args:
            key: Metadata key
            default: Default value if not found

        Returns:
            Metadata value
        """
        return self.metadata.get(key, default)

    def set_metadata(self, key, value):
        """
        Set metadata value

        Args:
            key: Metadata key
            value: Metadata value

        Example:
            branch.set_metadata('capacity', 500)
        """
        self.metadata[key] = value
        self.save(update_fields=["metadata"])

    def get_all_metadata(self):
        """
        Get all metadata

        Returns:
            Dictionary of metadata
        """
        return self.metadata.copy()

    def get_user_count(self):
        """
        Get number of users in this branch

        Returns:
            Integer count
        """
        from accounts.models.user_accounts import UserAccount

        return UserAccount.objects.filter(branch=self).count()

    def get_active_user_count(self):
        """
        Get number of active users in this branch

        Returns:
            Integer count
        """
        from accounts.models.user_accounts import UserAccount

        return UserAccount.objects.filter(branch=self, is_active=True).count()

    @classmethod
    def get_active_branches(cls, tenant):
        """
        Get all active branches for a tenant

        Args:
            tenant: Tenant instance

        Returns:
            QuerySet of Branch objects

        Example:
            branches = Branch.get_active_branches(tenant)
        """
        return cls.objects.filter(tenant=tenant, is_active=True).order_by("code")

    @classmethod
    def get_by_code(cls, tenant, code):
        """
        Get branch by code

        Args:
            tenant: Tenant instance
            code: Branch code

        Returns:
            Branch instance or None

        Example:
            branch = Branch.get_by_code(tenant, 'HCM')
        """
        return cls.objects.filter(tenant=tenant, code=code).first()


class BranchAuditLog(models.Model):
    """
    Audit log for branch changes

    Features:
    - Track branch creation, updates, and deletions
    - Record who made changes and when
    - Support for compliance audits
    """

    ACTION_CHOICES = (
        ("CREATE", _("Create - Branch created")),
        ("UPDATE", _("Update - Branch modified")),
        ("DELETE", _("Delete - Branch deleted")),
        ("ACTIVATE", _("Activate - Branch activated")),
        ("DEACTIVATE", _("Deactivate - Branch deactivated")),
    )

    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="branch_audit_logs",
        db_index=True,
        help_text="Tenant that owns this audit log",
    )

    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name="branch_audit_logs",
        null=True,
        blank=True,
        help_text="Branch affected by this change",
    )

    # ========================================================================
    # ACTION DETAILS
    # ========================================================================

    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        db_index=True,
        help_text="Type of action performed",
    )

    actor = models.ForeignKey(
        "accounts.UserAccount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="branch_actions_performed",
        help_text="User who performed the action",
    )
    actor_username = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        help_text="Username who performed the action",
    )

    # ========================================================================
    # CHANGE DETAILS
    # ========================================================================

    old_values = models.JSONField(null=True, blank=True, help_text="Previous values")
    new_values = models.JSONField(null=True, blank=True, help_text="New values")

    reason = models.TextField(blank=True, null=True, help_text="Reason for the change")

    # ========================================================================
    # TIMESTAMPS
    # ========================================================================

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "branch_audit_logs"
        verbose_name = _("Branch Audit Log")
        verbose_name_plural = _("Branch Audit Logs")
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["tenant", "created_at"], name="idx_branch_audit_tenant_created"
            ),
            models.Index(
                fields=["branch", "created_at"], name="idx_branch_audit_branch_created"
            ),
        ]

    def __str__(self):
        return f"{self.action} - {self.branch.code if self.branch else 'N/A'}"

    @classmethod
    def log_action(
        cls,
        tenant,
        branch,
        action,
        actor=None,
        actor_username=None,
        old_values=None,
        new_values=None,
        reason=None,
    ):
        """
        Log a branch action

        Args:
            tenant: Tenant instance
            branch: Branch instance
            action: Action type
            actor: UserAccount instance
            actor_username: Username
            old_values: Previous values
            new_values: New values
            reason: Reason for action

        Returns:
            BranchAuditLog instance
        """
        return cls.objects.create(
            tenant=tenant,
            branch=branch,
            action=action,
            actor=actor,
            actor_username=actor_username,
            old_values=old_values,
            new_values=new_values,
            reason=reason,
        )
