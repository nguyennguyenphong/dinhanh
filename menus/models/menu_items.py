# ============================================================================
# FILE: apps/menu/models.py
# Enhanced Menu Items Models with URL Routing
# ============================================================================

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class MenuItem(models.Model):
    """
    Enhanced menu item model with URL routing and badges

    Features:
    - Hierarchical structure: Support for nested menus (parent-child)
    - URL routing: Support Django URL names and static paths
    - Badge system: Display notifications, badges, status
    - Permission-based: Show items based on user permissions
    - Icon support: SVG paths or icon names
    - Sorting: Control display order
    - Status tracking: Active/inactive and hidden items
    - Metadata: Store additional configuration
    - Audit trail: Track creation and updates

    URL Resolution Strategy:
    1. Try to resolve url_name using Django reverse()
    2. Fall back to url_path if url_name fails
    3. Return None if both fail

    Badge System:
    - badge_text: Display text ("NEW", "BETA", "5", etc.)
    - badge_color: Hex color code (default: red #EF4444)
    - Can be used for notifications, status, labels

    Visibility:
    - is_active: Item is visible and accessible
    - is_hidden: Item is hidden from menu but route still works
    - permission_code: Required permission to view item

    Example:
        item = MenuItem.objects.create(
            tenant=tenant,
            group=group,
            code='ticket_list',
            label='Danh sách vé',
            url_name='tickets:list',
            url_path='/tickets/list',
            icon='mdi-list',
            badge_text='5',
            badge_color='#EF4444',
            permission_code='tickets.view_ticket',
            sort_order=1,
            open_in_new_tab=False
        )
    """

    id = models.AutoField(primary_key=True)

    # ========================================================================
    # MULTI-TENANT RELATIONSHIP
    # ========================================================================

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="menu_items",
        db_index=True,
        help_text="Tenant that owns this menu item",
    )

    # ========================================================================
    # HIERARCHY
    # ========================================================================

    group = models.ForeignKey(
        "MenuGroup",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="menu_items",
        db_index=True,
        help_text="Menu group this item belongs to",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        db_index=True,
        help_text="Parent menu item (for nested menus)",
    )

    # ========================================================================
    # IDENTIFICATION
    # ========================================================================

    code = models.CharField(
        max_length=80,
        validators=[
            RegexValidator(
                regex=r"^[a-z0-9_]+$",
                message="Code must contain only lowercase letters, numbers, and underscores",
            )
        ],
        help_text="Unique code for the menu item",
    )
    label = models.CharField(
        max_length=150, help_text="Display label for the menu item"
    )

    # ========================================================================
    # URL ROUTING
    # ========================================================================

    url_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text='Django URL name or route name (e.g., "tickets:list")',
    )
    url_path = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        help_text='Static URL path fallback (e.g., "/tickets/list")',
    )

    # ========================================================================
    # DISPLAY
    # ========================================================================

    icon = models.TextField(
        blank=True,
        null=True,
        help_text='SVG path string or icon name (e.g., "mdi-list")',
    )

    # ========================================================================
    # BADGE SYSTEM
    # ========================================================================

    badge_text = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        help_text='Badge text (e.g., "NEW", "BETA", "5" for notifications)',
    )
    badge_color = models.CharField(
        max_length=7,
        default="#EF4444",
        validators=[
            RegexValidator(
                regex=r"^#[0-9A-Fa-f]{6}$",
                message="Badge color must be a valid hex color (e.g., #EF4444)",
            )
        ],
        help_text="Badge color in hex format (default: red #EF4444)",
    )

    # ========================================================================
    # PERMISSIONS
    # ========================================================================

    permission_code = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        db_index=True,
        help_text="Required permission code to view this item",
    )

    # ========================================================================
    # SORTING & DISPLAY
    # ========================================================================

    sort_order = models.SmallIntegerField(
        default=0, db_index=True, help_text="Display order (lower values appear first)"
    )
    open_in_new_tab = models.BooleanField(
        default=False, help_text="Open URL in new tab/window"
    )

    # ========================================================================
    # STATUS
    # ========================================================================

    is_active = models.BooleanField(
        default=True, db_index=True, help_text="Menu item is active and visible"
    )
    is_hidden = models.BooleanField(
        default=False, help_text="Item is hidden from menu but route still works"
    )

    # ========================================================================
    # TIMESTAMPS
    # ========================================================================

    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, help_text="When this menu item was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="When this menu item was last updated"
    )

    class Meta:
        db_table = "menu_items"
        verbose_name = _("Menu Item")
        verbose_name_plural = _("Menu Items")
        ordering = ["sort_order", "code"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Unique code per tenant
            models.UniqueConstraint(
                fields=["tenant", "code"],
                name="unique_tenant_menu_item_code",
                violation_error_message="Menu item code must be unique within tenant",
            ),
        ]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Index for finding active items
            models.Index(
                fields=["tenant", "is_active"], name="idx_menu_item_tenant_active"
            ),
            # Index for group queries
            models.Index(
                fields=["group", "is_active"], name="idx_menu_item_group_active"
            ),
            # Index for parent-child queries
            models.Index(
                fields=["parent", "sort_order"], name="idx_menu_item_parent_sort"
            ),
            # Index for permission queries
            models.Index(fields=["permission_code"], name="idx_menu_item_permission"),
            # Index for hidden items
            models.Index(fields=["is_hidden"], name="idx_menu_item_hidden"),
        ]

    def __str__(self):
        """String representation"""
        prefix = "├─ " if self.parent else ""
        return f"{prefix}{self.label} ({self.code})"

    def clean(self):
        """
        Validate menu item
        """
        # Check tenant consistency
        if self.group and self.group.tenant_id != self.tenant_id:
            raise ValidationError("Menu item and group must belong to same tenant")

        # Check parent tenant consistency
        if self.parent and self.parent.tenant_id != self.tenant_id:
            raise ValidationError("Parent menu item must belong to same tenant")

        # Check circular reference
        if self.parent == self:
            raise ValidationError("Menu item cannot be its own parent")

        # Check circular hierarchy
        current = self.parent
        while current:
            if current == self:
                raise ValidationError("Circular menu hierarchy detected")
            current = current.parent

        # Validate at least one URL is provided
        if not self.url_name and not self.url_path:
            raise ValidationError("Either url_name or url_path must be provided")

    def save(self, *args, **kwargs):
        """Override save to enforce business rules"""
        self.clean()
        super().save(*args, **kwargs)

    # ========================================================================
    # URL RESOLUTION
    # ========================================================================

    def get_url(self):
        """
        Get resolved URL for this menu item

        Resolution strategy:
        1. Try to resolve url_name using Django reverse()
        2. Fall back to url_path if url_name fails
        3. Return None if both fail

        Returns:
            String URL or None

        Example:
            url = item.get_url()
            # Returns: '/tickets/list' or '/admin/tickets/'
        """
        # Try url_name first
        if self.url_name:
            try:
                return reverse(self.url_name)
            except Exception:
                pass

        # Fall back to url_path
        if self.url_path:
            return self.url_path

        return None

    def get_url_with_params(self, **params):
        """
        Get URL with parameters

        Args:
            **params: URL parameters

        Returns:
            String URL with parameters

        Example:
            url = item.get_url_with_params(ticket_id=123)
        """
        url = self.get_url()
        if not url:
            return None

        if params:
            # Build query string
            query_string = "&".join(f"{k}={v}" for k, v in params.items())
            return f"{url}?{query_string}"

        return url

    # ========================================================================
    # HIERARCHY METHODS
    # ========================================================================

    def get_children(self):
        """
        Get all active child items

        Returns:
            QuerySet of MenuItem objects
        """
        return self.children.filter(is_active=True).order_by("sort_order")

    def get_breadcrumb(self):
        """
        Get breadcrumb path from root to this item

        Returns:
            List of MenuItem objects

        Example:
            breadcrumb = item.get_breadcrumb()
            # Returns: [root_item, parent_item, item]
        """
        breadcrumb = [self]
        current = self.parent

        while current:
            breadcrumb.insert(0, current)
            current = current.parent

        return breadcrumb

    def get_breadcrumb_labels(self):
        """
        Get breadcrumb labels as string

        Returns:
            String like "Root > Parent > Item"
        """
        breadcrumb = self.get_breadcrumb()
        return " > ".join([item.label for item in breadcrumb])

    def get_depth(self):
        """
        Get depth in hierarchy (0 = root)

        Returns:
            Integer depth
        """
        depth = 0
        current = self.parent

        while current:
            depth += 1
            current = current.parent

        return depth

    # ========================================================================
    # PERMISSION METHODS
    # ========================================================================

    def has_permission(self, user):
        """
        Check if user has permission to view this item

        Args:
            user: UserAccount instance

        Returns:
            Boolean

        Example:
            if item.has_permission(user):
                # Show item
        """
        # Superuser has all permissions
        if user.is_superuser:
            return True

        # No permission required
        if not self.permission_code:
            return True

        # Check user permission
        return user.has_permission(self.permission_code)

    # ========================================================================
    # BADGE METHODS
    # ========================================================================

    def has_badge(self):
        """
        Check if item has badge

        Returns:
            Boolean
        """
        return bool(self.badge_text)

    def get_badge_data(self):
        """
        Get badge data as dictionary

        Returns:
            Dictionary with badge info or None

        Example:
            badge = item.get_badge_data()
            # Returns: {'text': '5', 'color': '#EF4444'}
        """
        if not self.has_badge():
            return None

        return {"text": self.badge_text, "color": self.badge_color}

    # ========================================================================
    # VISIBILITY METHODS
    # ========================================================================

    def is_visible(self):
        """
        Check if item is visible in menu

        Returns:
            Boolean
        """
        return self.is_active and not self.is_hidden

    def is_accessible(self):
        """
        Check if item route is accessible (even if hidden)

        Returns:
            Boolean
        """
        return self.is_active

    # ========================================================================
    # SERIALIZATION
    # ========================================================================

    def to_dict(self, user=None, include_children=True):
        """
        Convert menu item to dictionary

        Args:
            user: UserAccount instance (optional, for permission filtering)
            include_children: Include child items

        Returns:
            Dictionary representation

        Example:
            item_dict = item.to_dict(user)
            # Returns: {
            #     'id': 1,
            #     'code': 'ticket_list',
            #     'label': 'Danh sách vé',
            #     'url': '/tickets/list',
            #     'icon': 'mdi-list',
            #     'badge': {'text': '5', 'color': '#EF4444'},
            #     'children': [...]
            # }
        """
        item_dict = {
            "id": self.id,
            "code": self.code,
            "label": self.label,
            "url": self.get_url(),
            "icon": self.icon,
            "sort_order": self.sort_order,
            "open_in_new_tab": self.open_in_new_tab,
        }

        # Add badge if present
        badge = self.get_badge_data()
        if badge:
            item_dict["badge"] = badge

        # Add children if requested
        if include_children:
            children = self.get_children()
            if children.exists():
                item_dict["children"] = [
                    child.to_dict(user, include_children=True) for child in children
                ]

        return item_dict

    # ========================================================================
    # QUERY METHODS
    # ========================================================================

    @classmethod
    def get_visible_items(cls, tenant, user=None):
        """
        Get all visible menu items for a tenant

        Args:
            tenant: Tenant instance
            user: UserAccount instance (optional)

        Returns:
            QuerySet of MenuItem objects
        """
        items = cls.objects.filter(tenant=tenant, is_active=True, is_hidden=False)

        # Filter by permission if user provided
        if user and not user.is_superuser:
            # Get user permissions
            user_perms = set(user.get_permissions().values_list("codename", flat=True))

            # Filter items
            items = items.filter(
                models.Q(permission_code__isnull=True)
                | models.Q(permission_code__in=user_perms)
            )

        return items.order_by("sort_order")

    @classmethod
    def get_menu_tree(cls, tenant, user=None):
        """
        Get complete menu tree for a tenant

        Args:
            tenant: Tenant instance
            user: UserAccount instance (optional)

        Returns:
            List of root items with children

        Example:
            tree = MenuItem.get_menu_tree(tenant, user)
        """
        items = cls.get_visible_items(tenant, user)

        # Get root items (no parent)
        root_items = items.filter(parent__isnull=True)

        return list(root_items)

    @classmethod
    def get_menu_json(cls, tenant, user=None):
        """
        Get menu structure as JSON-serializable data

        Args:
            tenant: Tenant instance
            user: UserAccount instance (optional)

        Returns:
            List of dictionaries
        """
        tree = cls.get_menu_tree(tenant, user)

        return [item.to_dict(user, include_children=True) for item in tree]

    @classmethod
    def get_by_code(cls, tenant, code):
        """
        Get menu item by code

        Args:
            tenant: Tenant instance
            code: Menu item code

        Returns:
            MenuItem instance or None
        """
        return cls.objects.filter(tenant=tenant, code=code).first()

    @classmethod
    def get_by_url_name(cls, tenant, url_name):
        """
        Get menu items by URL name

        Args:
            tenant: Tenant instance
            url_name: Django URL name

        Returns:
            QuerySet of MenuItem objects
        """
        return cls.objects.filter(tenant=tenant, url_name=url_name, is_active=True)
