# ============================================================================
# FILE: apps/accounts/models.py
# Permission Models with Multi-Tenant Support
# ============================================================================

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Permission(models.Model):
    """
    Permission model for fine-grained access control in multi-tenant system

    Features:
    - Multi-tenant support: Permissions are tenant-specific
    - Module-based organization: Permissions grouped by functional modules
    - Action-based naming: Standard CRUD operations plus custom actions
    - Unique codename: Combination of module and action (e.g., 'tickets.add_ticket')
    - Hierarchical permissions: Support for parent-child permission relationships
    - System permissions: Built-in permissions that cannot be modified
    - Soft delete: Inactive permissions can be archived instead of deleted

    Permission Code Format: module.action_resource
    Examples:
        - tickets.view_ticket
        - tickets.add_ticket
        - tickets.change_ticket
        - tickets.delete_ticket
        - tickets.export_ticket
        - tickets.approve_ticket
        - vehicles.manage_all
        - reports.view_all

    Action Types:
        - view: Read/view access to resource
        - add: Create/add new resource
        - change: Update/modify existing resource
        - delete: Remove resource
        - export: Export data
        - approve: Approve/confirm actions
        - all: Full access to module
    """

    # Action choices with descriptions
    ACTION_CHOICES = (
        ("view", _("View - Read/view access to resources")),
        ("add", _("Add - Create/add new resources")),
        ("change", _("Change - Update/modify existing resources")),
        ("delete", _("Delete - Remove resources")),
        ("export", _("Export - Export data to external formats")),
        ("approve", _("Approve - Approve/confirm actions")),
        ("all", _("All - Full access to module")),
    )

    id = models.AutoField(primary_key=True)

    # ========================================================================
    # MULTI-TENANT RELATIONSHIP
    # ========================================================================

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="permissions",
        db_index=True,
        help_text="Tenant that owns this permission",
    )

    # ========================================================================
    # PERMISSION IDENTIFICATION
    # ========================================================================

    codename = models.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r"^[a-z0-9._-]+$",
                message="Codename must contain only lowercase letters, numbers, dots, underscores, and hyphens",
            )
        ],
        help_text='Unique permission code (e.g., "tickets.add_ticket", "vehicles.change_vehicle")',
    )
    name = models.CharField(
        max_length=255,
        help_text='Human-readable permission name (e.g., "Can add ticket")',
    )

    # ========================================================================
    # PERMISSION ORGANIZATION
    # ========================================================================

    module = models.CharField(
        max_length=100,
        db_index=True,
        help_text='Module name (e.g., "tickets", "vehicles", "hr", "reports")',
    )
    action = models.CharField(
        max_length=30,
        choices=ACTION_CHOICES,
        default="view",
        help_text="Action type (view, add, change, delete, export, approve, all)",
    )

    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed description of what this permission allows",
    )

    # ========================================================================
    # PERMISSION HIERARCHY
    # ========================================================================

    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        help_text="Parent permission (for hierarchical permissions)",
    )

    # ========================================================================
    # STATUS AND METADATA
    # ========================================================================

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Inactive permissions cannot be assigned to roles",
    )
    is_system = models.BooleanField(
        default=False,
        help_text="System permissions are predefined and cannot be modified",
    )

    # ========================================================================
    # TIMESTAMPS
    # ========================================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When this permission was created",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this permission was last updated",
    )

    class Meta:
        db_table = "permissions"
        verbose_name = _("Permission")
        verbose_name_plural = _("Permissions")
        ordering = ["module", "action", "codename"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Unique constraint: codename must be unique per tenant
            models.UniqueConstraint(
                fields=["tenant", "codename"],
                name="unique_tenant_permission_codename",
                violation_error_message="Permission codename must be unique within tenant",
            ),
            # Check constraint: validate action values
            models.CheckConstraint(
                condition=models.Q(
                    action__in=[
                        "view",
                        "add",
                        "change",
                        "delete",
                        "export",
                        "approve",
                        "all",
                    ]
                ),
                name="chk_permission_action",
            ),
        ]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Composite index for common queries
            models.Index(
                fields=["tenant", "module"],
                name="idx_permission_tenant_module",
            ),
            # Index for active permissions
            models.Index(
                fields=["tenant", "is_active"],
                name="idx_permission_tenant_active",
            ),
            # Index for system permissions
            models.Index(
                fields=["is_system"],
                name="idx_permission_is_system",
            ),
            # Composite index for role queries
            models.Index(
                fields=["tenant", "action"],
                name="idx_permission_tenant_action",
            ),
        ]

    def __str__(self):
        """String representation of permission"""
        return f"{self.codename} ({self.tenant.code})"

    def save(self, *args, **kwargs):
        """
        Override save to enforce business rules

        Rules:
        - Codename must be lowercase
        - System permissions cannot be modified after creation
        - Parent permission must belong to same tenant
        """
        # Enforce lowercase codename
        self.codename = self.codename.lower()

        # Validate parent permission
        if self.parent and self.parent.tenant_id != self.tenant_id:
            raise ValidationError("Parent permission must belong to the same tenant")

        # Prevent modification of system permissions
        if self.is_system and self.pk:
            existing = Permission.objects.get(pk=self.pk)
            if existing.is_system and (
                existing.codename != self.codename or existing.action != self.action
            ):
                raise ValidationError("System permissions cannot be modified")

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Override delete to prevent deletion of system permissions
        """
        if self.is_system:
            raise ValidationError("System permissions cannot be deleted")
        super().delete(*args, **kwargs)

    @classmethod
    def get_by_codename(cls, tenant, codename):
        """
        Get permission by codename for specific tenant

        Args:
            tenant: Tenant instance
            codename: Permission codename (e.g., 'tickets.add_ticket')

        Returns:
            Permission instance or None

        Example:
            perm = Permission.get_by_codename(tenant, 'tickets.add_ticket')
        """
        return cls.objects.filter(
            tenant=tenant, codename=codename, is_active=True
        ).first()

    @classmethod
    def get_by_module(cls, tenant, module):
        """
        Get all permissions for specific module

        Args:
            tenant: Tenant instance
            module: Module name (e.g., 'tickets')

        Returns:
            QuerySet of Permission objects

        Example:
            perms = Permission.get_by_module(tenant, 'tickets')
        """
        return cls.objects.filter(
            tenant=tenant, module=module, is_active=True
        ).order_by("action")

    @classmethod
    def get_by_action(cls, tenant, action):
        """
        Get all permissions for specific action

        Args:
            tenant: Tenant instance
            action: Action type (e.g., 'view', 'add')

        Returns:
            QuerySet of Permission objects

        Example:
            perms = Permission.get_by_action(tenant, 'view')
        """
        return cls.objects.filter(
            tenant=tenant, action=action, is_active=True
        ).order_by("module")

    @classmethod
    def get_by_module_and_action(cls, tenant, module, action):
        """
        Get specific permission by module and action

        Args:
            tenant: Tenant instance
            module: Module name
            action: Action type

        Returns:
            Permission instance or None

        Example:
            perm = Permission.get_by_module_and_action(tenant, 'tickets', 'view')
        """
        return cls.objects.filter(
            tenant=tenant, module=module, action=action, is_active=True
        ).first()

    def get_children(self):
        """
        Get all child permissions (hierarchical)

        Returns:
            QuerySet of child Permission objects
        """
        return self.children.filter(is_active=True)

    def get_all_descendants(self):
        """
        Get all descendant permissions recursively

        Returns:
            QuerySet of all descendant Permission objects
        """
        descendants = set()

        def collect_descendants(perm):
            for child in perm.children.filter(is_active=True):
                descendants.add(child)
                collect_descendants(child)

        collect_descendants(self)
        return Permission.objects.filter(pk__in=[p.pk for p in descendants])

    def has_parent(self, parent_codename):
        """
        Check if this permission has specific parent (hierarchical)

        Args:
            parent_codename: Parent permission codename

        Returns:
            Boolean
        """
        current = self.parent
        while current:
            if current.codename == parent_codename:
                return True
            current = current.parent
        return False

    @property
    def full_codename(self):
        """
        Get full hierarchical codename

        Returns:
            String like 'tickets.view_all' or 'tickets.view_ticket'
        """
        return self.codename

    def get_description_display(self):
        """
        Get formatted description for display

        Returns:
            String with description or default message
        """
        if self.description:
            return self.description

        action_desc = dict(self.ACTION_CHOICES).get(self.action, self.action)
        return f"{action_desc} in {self.module} module"
