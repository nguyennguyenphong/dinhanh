# Sort
SORT_CHOICES = [
    ("", "Sắp xếp theo"),
    ("az", "Tên: A → Z"),
    ("za", "Tên: Z → A"),
    ("latest", "Mới nhất"),
    ("oldest", "Cũ nhất"),
]

# Status
STATUS_CHOICES = (
    ("True", "Kích hoạt"),
    ("False", "Khóa"),
)


"""
Constants for the menu_groups application.
"""

# ============================================================================
# AUDIT ACTIONS
# ============================================================================


class MenuAuditAction:
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    REORDER = "REORDER"

    CHOICES = (
        (CREATE, "Create - Menu item created"),
        (UPDATE, "Update - Menu item modified"),
        (DELETE, "Delete - Menu item deleted"),
        (REORDER, "Reorder - Menu items reordered"),
    )


class MenuItemRoleAuditAction:
    ASSIGN = "ASSIGN"
    REVOKE = "REVOKE"
    BATCH_ASSIGN = "BATCH_ASSIGN"
    BATCH_REVOKE = "BATCH_REVOKE"

    CHOICES = (
        (ASSIGN, "Assign - Role assigned to menu item"),
        (REVOKE, "Revoke - Role revoked from menu item"),
        (BATCH_ASSIGN, "Batch Assign - Multiple roles assigned"),
        (BATCH_REVOKE, "Batch Revoke - Multiple roles revoked"),
    )


# ============================================================================
# CACHE KEYS
# ============================================================================


class CacheKey:
    MENU_ITEM_ROLES = "menu_item_{menu_item_id}_roles"
    ROLE_MENU_ITEMS = "role_{role_id}_menu_items"
    TENANT_MENU_TREE = "tenant_{tenant_id}_menu_tree"
    USER_MENU = "user_{user_id}_tenant_{tenant_id}_menu"

    # Cache TTLs (in seconds)
    TTL_SHORT = 60 * 5  # 5 minutes
    TTL_MEDIUM = 60 * 30  # 30 minutes
    TTL_LONG = 60 * 60 * 2  # 2 hours


# ============================================================================
# PAGINATION
# ============================================================================


class Pagination:
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100


# ============================================================================
# MENU GROUP DEFAULTS
# ============================================================================


class MenuGroupDefaults:
    SORT_ORDER = 0
    IS_ACTIVE = True


# ============================================================================
# MENU ITEM DEFAULTS
# ============================================================================


class MenuItemDefaults:
    SORT_ORDER = 0
    IS_ACTIVE = True
    IS_HIDDEN = False
    OPEN_IN_NEW_TAB = False
    BADGE_COLOR = "#EF4444"


# ============================================================================
# VALIDATION
# ============================================================================


class Validation:
    CODE_PATTERN_GROUP = r"^[a-z0-9_]+$"
    CODE_PATTERN_ITEM = r"^[a-z0-9_]+$"
    HEX_COLOR_PATTERN = r"^#[0-9A-Fa-f]{6}$"
    MAX_HIERARCHY_DEPTH = 5


# ============================================================================
# MESSAGES
# ============================================================================


class Messages:
    MENU_GROUP_CREATED = "Menu group '{label}' created successfully."
    MENU_GROUP_UPDATED = "Menu group '{label}' updated successfully."
    MENU_GROUP_DELETED = "Menu group '{label}' deleted successfully."
    MENU_GROUP_NOT_FOUND = "Menu group not found."
    MENU_GROUP_CODE_EXISTS = "Menu group with this code already exists in the tenant."

    MENU_ITEM_CREATED = "Menu item '{label}' created successfully."
    MENU_ITEM_UPDATED = "Menu item '{label}' updated successfully."
    MENU_ITEM_DELETED = "Menu item '{label}' deleted successfully."
    MENU_ITEM_NOT_FOUND = "Menu item not found."
    MENU_ITEM_CODE_EXISTS = "Menu item with this code already exists in the tenant."
    MENU_ITEM_CIRCULAR = "Circular menu hierarchy detected."
    MENU_ITEM_MAX_DEPTH = (
        f"Maximum menu hierarchy depth ({Validation.MAX_HIERARCHY_DEPTH}) exceeded."
    )

    ROLE_ASSIGNED = "Role assigned to menu item successfully."
    ROLE_REVOKED = "Role revoked from menu item successfully."
    ROLES_BATCH_ASSIGNED = "{count} role(s) assigned to menu item."
    ROLES_BATCH_REVOKED = "All roles revoked from menu item."
    ROLE_ALREADY_ASSIGNED = "Role is already assigned to this menu item."
