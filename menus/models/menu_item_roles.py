# ============================================================================
# FILE: apps/menu/models.py
# Menu Item Roles Models with Role-Based Visibility
# ============================================================================

import uuid

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class MenuItemRole(BaseModel):
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

    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    menu_item = models.ForeignKey(
        "menus.MenuItem",
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
