# ============================================================================
# FILE: apps/menu/models.py
# Menu Item Roles Models with Role-Based Visibility
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from django.core.exceptions import ValidationError
from tenants.models.tenants import Tenant


class MenuItemRole(models.Model):
    """
    Through model for Menu Item-Role many-to-many relationship

    Features:
    - Role-based menu visibility: Show menu items based on user roles
    - Multi-role support: Menu item can be visible to multiple roles
    - Flexible access control: Combine with permission_code for granular control
    - Caching: Cache menu visibility per role for performance
    - Audit trail: Track role assignments

    Access Control Strategy:
    1. If permission_code is set: User must have the permission
    2. If roles are assigned: User must have one of the roles
    3. If neither: Item is visible to all users

    Visibility Logic:
    - If roles are assigned: Only users with those roles see the item
    - If no roles assigned: Item is visible to all (unless permission_code blocks it)
    - Superusers always see items (unless explicitly hidden)

    Example:
        # Assign role to menu item
        MenuItemRole.objects.create(
            menu_item=item,
            role=manager_role
        )

        # Get visible items for user
        items = MenuItem.get_visible_for_user(user)

        # Check if item is visible to role
        is_visible = MenuItemRole.is_visible_to_role(item, role)
    """

    menu_item = models.ForeignKey(
        "MenuItem",
        on_delete=models.CASCADE,
        related_name="role_assignments",
        db_index=True,
        help_text="Menu item assigned to this role",
    )
    role = models.ForeignKey(
        "accounts.Role",
        on_delete=models.CASCADE,
        related_name="menu_item_assignments",
        db_index=True,
        help_text="Role that can access this menu item",
    )

    class Meta:
        db_table = "menu_item_roles"
        verbose_name = _("Menu Item Role")
        verbose_name_plural = _("Menu Item Roles")

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Primary key: menu_item_id + role_id
            models.UniqueConstraint(
                fields=["menu_item", "role"],
                name="unique_menu_item_role",
                violation_error_message="This role is already assigned to this menu item",
            ),
        ]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Index for finding roles for a menu item
            models.Index(
                fields=["menu_item"],
                name="idx_menu_item_role_item",
            ),
            # Index for finding menu items for a role
            models.Index(
                fields=["role"],
                name="idx_menu_item_role_role",
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.menu_item.label} -> {self.role.slug}"

    def clean(self):
        """
        Validate menu item role assignment
        """
        # Check tenant consistency
        if self.menu_item.tenant_id != self.role.tenant_id:
            raise ValidationError("Menu item and role must belong to same tenant")

    def save(self, *args, **kwargs):
        """Override save to enforce business rules"""
        self.clean()

        # Clear cache when assignment changes
        self._clear_cache()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Override delete to clear cache"""
        self._clear_cache()
        super().delete(*args, **kwargs)

    def _clear_cache(self):
        """Clear related cache entries"""
        # Clear menu item cache
        cache_key = f"menu_item_{self.menu_item_id}_roles"
        cache.delete(cache_key)

        # Clear role cache
        cache_key = f"role_{self.role_id}_menu_items"
        cache.delete(cache_key)

    @classmethod
    def assign_role(cls, menu_item, role):
        """
        Assign role to menu item

        Args:
            menu_item: MenuItem instance
            role: Role instance

        Returns:
            Tuple (MenuItemRole, created)

        Example:
            assignment, created = MenuItemRole.assign_role(item, role)
        """
        assignment, created = cls.objects.get_or_create(menu_item=menu_item, role=role)
        return assignment, created

    @classmethod
    def revoke_role(cls, menu_item, role):
        """
        Revoke role from menu item

        Args:
            menu_item: MenuItem instance
            role: Role instance

        Returns:
            Number of deleted assignments
        """
        count, _ = cls.objects.filter(menu_item=menu_item, role=role).delete()
        return count

    @classmethod
    def assign_roles_batch(cls, menu_item, roles):
        """
        Assign multiple roles to menu item

        Args:
            menu_item: MenuItem instance
            roles: List of Role instances

        Returns:
            List of created MenuItemRole instances

        Example:
            roles = Role.objects.filter(is_system=False)
            assignments = MenuItemRole.assign_roles_batch(item, roles)
        """
        assignments = []
        for role in roles:
            assignment, _ = cls.assign_role(menu_item, role)
            assignments.append(assignment)
        return assignments

    @classmethod
    def revoke_all_roles(cls, menu_item):
        """
        Revoke all roles from menu item

        Args:
            menu_item: MenuItem instance

        Returns:
            Number of deleted assignments
        """
        count, _ = cls.objects.filter(menu_item=menu_item).delete()
        return count

    @classmethod
    def get_roles_for_item(cls, menu_item):
        """
        Get all roles for a menu item

        Args:
            menu_item: MenuItem instance

        Returns:
            QuerySet of Role objects

        Example:
            roles = MenuItemRole.get_roles_for_item(item)
        """
        from accounts.models.roles import Role

        return Role.objects.filter(
            menu_item_assignments__menu_item=menu_item
        ).distinct()

    @classmethod
    def get_items_for_role(cls, role):
        """
        Get all menu items for a role

        Args:
            role: Role instance

        Returns:
            QuerySet of MenuItem objects

        Example:
            items = MenuItemRole.get_items_for_role(role)
        """
        from menus.models.menu_items import MenuItem

        return MenuItem.objects.filter(
            role_assignments__role=role, is_active=True
        ).distinct()

    @classmethod
    def is_visible_to_role(cls, menu_item, role):
        """
        Check if menu item is visible to role

        Args:
            menu_item: MenuItem instance
            role: Role instance

        Returns:
            Boolean

        Example:
            if MenuItemRole.is_visible_to_role(item, role):
                # Show item
        """
        # Check if roles are assigned
        has_roles = menu_item.role_assignments.exists()

        # If no roles assigned, visible to all
        if not has_roles:
            return True

        # Check if role is assigned
        return menu_item.role_assignments.filter(role=role).exists()

    @classmethod
    def get_visible_items_for_role(cls, tenant, role):
        """
        Get all visible menu items for a role

        Args:
            tenant: Tenant instance
            role: Role instance

        Returns:
            QuerySet of MenuItem objects

        Example:
            items = MenuItemRole.get_visible_items_for_role(tenant, role)
        """
        from menus.models.menu_items import MenuItem

        # Get items with no role restrictions
        no_role_items = MenuItem.objects.filter(
            tenant=tenant,
            is_active=True,
            is_hidden=False,
            role_assignments__isnull=True,
        )

        # Get items assigned to this role
        role_items = MenuItem.objects.filter(
            tenant=tenant, is_active=True, is_hidden=False, role_assignments__role=role
        )

        # Combine and remove duplicates
        return (no_role_items | role_items).distinct()


class MenuItemRoleAuditLog(models.Model):
    """
    Audit log for menu item role assignments

    Features:
    - Track role assignments and revocations
    - Record who made changes and when
    - Support for compliance audits
    """

    ACTION_CHOICES = (
        ("ASSIGN", _("Assign - Role assigned to menu item")),
        ("REVOKE", _("Revoke - Role revoked from menu item")),
        ("BATCH_ASSIGN", _("Batch Assign - Multiple roles assigned")),
        ("BATCH_REVOKE", _("Batch Revoke - Multiple roles revoked")),
    )

    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="menu_item_role_audit_logs",
        db_index=True,
        help_text="Tenant that owns this audit log",
    )

    menu_item = models.ForeignKey(
        "MenuItem",
        on_delete=models.CASCADE,
        related_name="role_audit_logs",
        db_index=True,
        help_text="Menu item affected by this change",
    )

    role = models.ForeignKey(
        "accounts.Role",
        on_delete=models.CASCADE,
        related_name="menu_item_audit_logs",
        null=True,
        blank=True,
        help_text="Role affected (null for batch operations)",
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
        related_name="menu_item_role_actions_performed",
        help_text="User who performed the action",
    )
    actor_username = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        help_text="Username who performed the action",
    )

    # ========================================================================
    # DETAILS
    # ========================================================================

    affected_count = models.IntegerField(
        default=1, help_text="Number of roles affected (for batch operations)"
    )

    reason = models.TextField(blank=True, null=True, help_text="Reason for the change")

    # ========================================================================
    # TIMESTAMPS
    # ========================================================================

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "menu_item_role_audit_logs"
        verbose_name = _("Menu Item Role Audit Log")
        verbose_name_plural = _("Menu Item Role Audit Logs")
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["tenant", "created_at"],
                name="idx_menu_item_role_audit_tenant_created",
            ),
            models.Index(
                fields=["menu_item", "created_at"],
                name="idx_menu_item_role_audit_item_created",
            ),
            models.Index(fields=["action"], name="idx_menu_item_role_audit_action"),
        ]

    def __str__(self):
        return f"{self.action} - {self.menu_item.label}"

    @classmethod
    def log_action(
        cls,
        tenant,
        menu_item,
        role=None,
        action="ASSIGN",
        actor=None,
        actor_username=None,
        affected_count=1,
        reason=None,
    ):
        """
        Log a menu item role action

        Args:
            tenant: Tenant instance
            menu_item: MenuItem instance
            role: Role instance (optional for batch)
            action: Action type
            actor: UserAccount instance
            actor_username: Username
            affected_count: Number of roles affected
            reason: Reason for action

        Returns:
            MenuItemRoleAuditLog instance
        """
        return cls.objects.create(
            tenant=tenant,
            menu_item=menu_item,
            role=role,
            action=action,
            actor=actor,
            actor_username=actor_username,
            affected_count=affected_count,
            reason=reason,
        )
