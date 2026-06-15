# ============================================================================
# FILE: apps/menu/models.py
# Menu Models with Hierarchical Structure
# ============================================================================

import uuid

from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from safedelete.models import SOFT_DELETE_CASCADE, SafeDeleteModel


class MenuGroup(SafeDeleteModel):
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

    _safedelete_policy = SOFT_DELETE_CASCADE

    id = models.AutoField(primary_key=True)

    # ========================================================================
    # MULTI-TENANT RELATIONSHIP
    # ========================================================================

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="menu_groups",
        db_index=True,
        help_text="Tenant that owns this menu group",
    )

    # ========================================================================
    # IDENTIFICATION
    # ========================================================================

    code = models.CharField(
        max_length=50,
        validators=[
            RegexValidator(
                regex=r"^[a-z0-9_]+$",
                message="Code must contain only lowercase letters, numbers, and underscores",
            )
        ],
        help_text='Unique code for the menu group (e.g., "operations", "hr")',
    )
    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    label = models.CharField(
        max_length=100,
        help_text='Display label for the menu group (e.g., "Vận hành xe")',
    )

    # ========================================================================
    # DISPLAY
    # ========================================================================

    icon = models.TextField(
        blank=True,
        null=True,
        help_text='SVG path string or icon name (e.g., "mdi-truck", "<svg>...</svg>")',
    )
    sort_order = models.SmallIntegerField(
        default=0, db_index=True, help_text="Display order (lower values appear first)"
    )

    # ========================================================================
    # STATUS
    # ========================================================================

    is_active = models.BooleanField(
        default=True, db_index=True, help_text="Menu group is active and visible"
    )

    # ========================================================================
    # TIMESTAMPS
    # ========================================================================

    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, help_text="When this menu group was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="When this menu group was last updated"
    )

    class Meta:
        db_table = "menu_groups"
        verbose_name = _("Menu Group")
        verbose_name_plural = _("Menu Groups")
        ordering = ["sort_order", "code"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Unique code per tenant
            models.UniqueConstraint(
                fields=["tenant", "code"],
                name="unique_tenant_menu_group_code",
                violation_error_message="Menu group code must be unique within tenant",
            ),
        ]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Index for finding active groups
            models.Index(
                fields=["tenant", "is_active"], name="idx_menu_group_tenant_active"
            ),
            # Index for sorting
            models.Index(
                fields=["tenant", "sort_order"], name="idx_menu_group_tenant_sort"
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
        return self.menu_items.filter(is_active=True).order_by("sort_order")

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
                models.Q(permission__isnull=True)
                | models.Q(permission__in=user.get_permissions())
            )

        return items.order_by("sort_order")
