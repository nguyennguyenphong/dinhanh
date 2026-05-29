# ============================================================================
# FILE: apps/menu/models.py
# Menu Models with Hierarchical Structure
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from tenants.models.tenants import Tenant


class MenuGroup(models.Model):
    """
    Menu group model for organizing menu items
    
    Features:
    - Multi-tenant support: Each tenant has own menu groups
    - Icon support: SVG paths or icon names
    - Sorting: Control display order
    - Status tracking: Active/inactive groups
    - Audit trail: Track creation and updates
    
    Use Cases:
    - Main menu sections (Operations, HR, Finance, etc.)
    - Grouping related menu items
    - Organizing navigation structure
    
    Example:
        group = MenuGroup.objects.create(
            tenant=tenant,
            code='operations',
            label='Vận hành xe',
            icon='<svg>...</svg>',
            sort_order=1
        )
    """

    id = models.AutoField(primary_key=True)
    
    # ========================================================================
    # MULTI-TENANT RELATIONSHIP
    # ========================================================================
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='menu_groups',
        db_index=True,
        help_text='Tenant that owns this menu group',
        db_comment='Reference to tenant'
    )
    
    # ========================================================================
    # IDENTIFICATION
    # ========================================================================
    
    code = models.CharField(
        max_length=50,
        validators=[
            RegexValidator(
                regex=r'^[a-z0-9_]+$',
                message='Code must contain only lowercase letters, numbers, and underscores'
            )
        ],
        help_text='Unique code for the menu group (e.g., "operations", "hr")',
        db_comment='Menu group code identifier'
    )
    label = models.CharField(
        max_length=100,
        help_text='Display label for the menu group (e.g., "Vận hành xe")',
        db_comment='Menu group display label'
    )
    
    # ========================================================================
    # DISPLAY
    # ========================================================================
    
    icon = models.TextField(
        blank=True,
        null=True,
        help_text='SVG path string or icon name (e.g., "mdi-truck", "<svg>...</svg>")',
        db_comment='Icon SVG or name'
    )
    sort_order = models.SmallIntegerField(
        default=0,
        db_index=True,
        help_text='Display order (lower values appear first)',
        db_comment='Sort order'
    )
    
    # ========================================================================
    # STATUS
    # ========================================================================
    
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text='Menu group is active and visible',
        db_comment='Active status'
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='When this menu group was created',
        db_comment='Creation timestamp'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='When this menu group was last updated',
        db_comment='Last update timestamp'
    )

    class Meta:
        db_table = 'menu_groups'
        verbose_name = _('Menu Group')
        verbose_name_plural = _('Menu Groups')
        ordering = ['sort_order', 'code']
        
        # ====================================================================
        # CONSTRAINTS
        # ====================================================================
        
        constraints = [
            # Unique code per tenant
            models.UniqueConstraint(
                fields=['tenant', 'code'],
                name='unique_tenant_menu_group_code',
                violation_error_message='Menu group code must be unique within tenant'
            ),
        ]
        
        # ====================================================================
        # INDEXES
        # ====================================================================
        
        indexes = [
            # Index for finding active groups
            models.Index(
                fields=['tenant', 'is_active'],
                name='idx_menu_group_tenant_active',
                db_comment='Query active menu groups by tenant'
            ),
            # Index for sorting
            models.Index(
                fields=['tenant', 'sort_order'],
                name='idx_menu_group_tenant_sort',
                db_comment='Query menu groups by tenant and sort order'
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.label} ({self.code})"

    def get_menu_items(self):
        """
        Get all active menu items in this group
        
        Returns:
            QuerySet of MenuItem objects
        """
        return self.menu_items.filter(is_active=True).order_by('sort_order')

    def get_menu_items_for_user(self, user):
        """
        Get menu items visible to a user (based on permissions)
        
        Args:
            user: UserAccount instance
        
        Returns:
            QuerySet of MenuItem objects
        """
        
        # Get items in this group
        items = self.menu_items.filter(is_active=True)
        
        # Filter by permissions if user is not superuser
        if not user.is_superuser:
            items = items.filter(
                models.Q(permission__isnull=True) |
                models.Q(permission__in=user.get_permissions())
            )
        
        return items.order_by('sort_order')


class MenuItem(models.Model):
    """
    Menu item model for individual menu entries
    
    Features:
    - Hierarchical structure: Support for parent-child items
    - Permission-based visibility: Show items based on user permissions
    - URL routing: Support for different URL types
    - Icon support: Individual item icons
    - Sorting: Control display order
    - Status tracking: Active/inactive items
    - Metadata: Store additional configuration
    
    URL Types:
    - 'internal': Internal Django URL (e.g., 'admin:index')
    - 'external': External URL (e.g., 'https://example.com')
    - 'route': Vue Router route (e.g., '/tickets/list')
    - 'action': Custom action handler
    
    Example:
        item = MenuItem.objects.create(
            tenant=tenant,
            group=group,
            code='ticket_list',
            label='Danh sách vé',
            url='/tickets/list',
            url_type='route',
            icon='mdi-list',
            sort_order=1,
            permission=permission
        )
    """

    URL_TYPE_CHOICES = (
        ('internal', _('Internal - Django admin URL')),
        ('external', _('External - External URL')),
        ('route', _('Route - Vue Router route')),
        ('action', _('Action - Custom action handler')),
    )

    id = models.AutoField(primary_key=True)
    
    # ========================================================================
    # MULTI-TENANT RELATIONSHIP
    # ========================================================================
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='menu_items',
        db_index=True,
        help_text='Tenant that owns this menu item',
        db_comment='Reference to tenant'
    )
    
    # ========================================================================
    # HIERARCHY
    # ========================================================================
    
    group = models.ForeignKey(
        MenuGroup,
        on_delete=models.CASCADE,
        related_name='menu_items',
        db_index=True,
        help_text='Menu group this item belongs to',
        db_comment='Reference to menu group'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        db_index=True,
        help_text='Parent menu item (for submenu)',
        db_comment='Parent menu item'
    )
    
    # ========================================================================
    # IDENTIFICATION
    # ========================================================================
    
    code = models.CharField(
        max_length=50,
        validators=[
            RegexValidator(
                regex=r'^[a-z0-9_]+$',
                message='Code must contain only lowercase letters, numbers, and underscores'
            )
        ],
        help_text='Unique code for the menu item',
        db_comment='Menu item code identifier'
    )
    label = models.CharField(
        max_length=100,
        help_text='Display label for the menu item',
        db_comment='Menu item display label'
    )
    
    # ========================================================================
    # URL CONFIGURATION
    # ========================================================================
    
    url = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text='URL or route for this menu item',
        db_comment='Menu item URL/route'
    )
    url_type = models.CharField(
        max_length=20,
        choices=URL_TYPE_CHOICES,
        default='route',
        help_text='Type of URL (internal, external, route, action)',
        db_comment='URL type'
    )
    
    # ========================================================================
    # DISPLAY
    # ========================================================================
    
    icon = models.TextField(
        blank=True,
        null=True,
        help_text='SVG path string or icon name',
        db_comment='Icon SVG or name'
    )
    badge = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Badge text (e.g., "NEW", "5")',
        db_comment='Badge text'
    )
    sort_order = models.SmallIntegerField(
        default=0,
        db_index=True,
        help_text='Display order',
        db_comment='Sort order'
    )
    
    # ========================================================================
    # PERMISSIONS
    # ========================================================================
    
    permission = models.ForeignKey(
        'accounts.Permission',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='menu_items',
        help_text='Required permission to view this item',
        db_comment='Required permission'
    )
    
    # ========================================================================
    # STATUS
    # ========================================================================
    
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text='Menu item is active and visible',
        db_comment='Active status'
    )
    
    # ========================================================================
    # METADATA
    # ========================================================================
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional configuration (e.g., target, params)',
        db_comment='Metadata JSON'
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='When this menu item was created',
        db_comment='Creation timestamp'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='When this menu item was last updated',
        db_comment='Last update timestamp'
    )

    class Meta:
        db_table = 'menu_items'
        verbose_name = _('Menu Item')
        verbose_name_plural = _('Menu Items')
        ordering = ['sort_order', 'code']
        
        # ====================================================================
        # CONSTRAINTS
        # ====================================================================
        
        constraints = [
            # Unique code per tenant and group
            models.UniqueConstraint(
                fields=['tenant', 'group', 'code'],
                name='unique_tenant_group_menu_item_code',
                violation_error_message='Menu item code must be unique within group'
            ),
        ]
        
        # ====================================================================
        # INDEXES
        # ====================================================================
        
        indexes = [
            # Index for finding active items
            models.Index(
                fields=['group', 'is_active'],
                name='idx_menu_item_group_active',
                db_comment='Query active menu items by group'
            ),
            # Index for parent-child queries
            models.Index(
                fields=['parent', 'sort_order'],
                name='idx_menu_item_parent_sort',
                db_comment='Query child items by parent and sort order'
            ),
            # Index for permission queries
            models.Index(
                fields=['permission'],
                name='idx_menu_item_permission',
                db_comment='Query menu items by permission'
            ),
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
        if self.group.tenant_id != self.tenant_id:
            raise ValidationError(
                'Menu item and group must belong to same tenant'
            )
        
        # Check parent tenant consistency
        if self.parent and self.parent.tenant_id != self.tenant_id:
            raise ValidationError(
                'Parent menu item must belong to same tenant'
            )
        
        # Check circular reference
        if self.parent == self:
            raise ValidationError(
                'Menu item cannot be its own parent'
            )
        
        # Check circular hierarchy
        current = self.parent
        while current:
            if current == self:
                raise ValidationError(
                    'Circular menu hierarchy detected'
                )
            current = current.parent

    def save(self, *args, **kwargs):
        """Override save to enforce business rules"""
        self.clean()
        super().save(*args, **kwargs)

    def get_children(self):
        """
        Get all active child items
        
        Returns:
            QuerySet of MenuItem objects
        """
        return self.children.filter(is_active=True).order_by('sort_order')

    def get_breadcrumb(self):
        """
        Get breadcrumb path from root to this item
        
        Returns:
            List of MenuItem objects
        """
        breadcrumb = [self]
        current = self.parent
        
        while current:
            breadcrumb.insert(0, current)
            current = current.parent
        
        return breadcrumb

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
        """
        self.metadata[key] = value
        self.save(update_fields=['metadata'])

    @classmethod
    def get_menu_tree(cls, tenant, user=None):
        """
        Get complete menu tree for a tenant
        
        Args:
            tenant: Tenant instance
            user: UserAccount instance (optional, for permission filtering)
        
        Returns:
            List of menu groups with items
        
        Example:
            menu_tree = MenuItem.get_menu_tree(tenant, user)
            # Returns: [
            #     {
            #         'group': MenuGroup,
            #         'items': [MenuItem, ...]
            #     },
            #     ...
            # ]
        """
        groups = MenuGroup.objects.filter(
            tenant=tenant,
            is_active=True
        ).order_by('sort_order')
        
        menu_tree = []
        
        for group in groups:
            if user:
                items = group.get_menu_items_for_user(user)
            else:
                items = group.get_menu_items()
            
            if items.exists():
                menu_tree.append({
                    'group': group,
                    'items': list(items)
                })
        
        return menu_tree

    @classmethod
    def get_menu_json(cls, tenant, user=None):
        """
        Get menu structure as JSON
        
        Args:
            tenant: Tenant instance
            user: UserAccount instance (optional)
        
        Returns:
            JSON-serializable dictionary
        """
        menu_tree = cls.get_menu_tree(tenant, user)
        
        result = []
        for group_data in menu_tree:
            group = group_data['group']
            items = group_data['items']
            
            group_dict = {
                'id': f"group_{group.id}",
                'code': group.code,
                'label': group.label,
                'icon': group.icon,
                'children': []
            }
            
            # Add root items
            root_items = items.filter(parent__isnull=True)
            for item in root_items:
                group_dict['children'].append(
                    cls._item_to_dict(item, items)
                )
            
            result.append(group_dict)
        
        return result

    @staticmethod
    def _item_to_dict(item, all_items):
        """
        Convert menu item to dictionary
        
        Args:
            item: MenuItem instance
            all_items: QuerySet of all items for context
        
        Returns:
            Dictionary representation
        """
        children = item.get_children()
        
        item_dict = {
            'id': f"item_{item.id}",
            'code': item.code,
            'label': item.label,
            'url': item.url,
            'url_type': item.url_type,
            'icon': item.icon,
            'badge': item.badge,
        }
        
        # Add children if any
        if children.exists():
            item_dict['children'] = [
                MenuItem._item_to_dict(child, all_items)
                for child in children
            ]
        
        return item_dict


class MenuAuditLog(models.Model):
    """
    Audit log for menu changes
    """
    
    ACTION_CHOICES = (
        ('CREATE', _('Create - Menu item created')),
        ('UPDATE', _('Update - Menu item modified')),
        ('DELETE', _('Delete - Menu item deleted')),
        ('REORDER', _('Reorder - Menu items reordered')),
    )

    id = models.BigAutoField(primary_key=True)
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='menu_audit_logs',
        db_index=True
    )
    
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        db_index=True
    )
    
    actor = models.ForeignKey(
        'accounts.UserAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='menu_actions_performed'
    )
    
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'menu_audit_logs'
        verbose_name = _('Menu Audit Log')
        verbose_name_plural = _('Menu Audit Logs')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} - {self.created_at}"