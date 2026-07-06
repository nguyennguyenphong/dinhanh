from menus.urls.menu_groups.urls import urlpatterns as menu_group_patterns
from menus.urls.menu_item_roles.urls import urlpatterns as menu_item_role_patterns
from menus.urls.menu_items.urls import urlpatterns as menu_item_patterns

urlpatterns = [
    *menu_group_patterns,
    *menu_item_patterns,
    *menu_item_role_patterns,
]
