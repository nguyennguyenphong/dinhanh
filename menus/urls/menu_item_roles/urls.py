from django.urls import path

from menus.views import menu_item_roles as menu_views

urlpatterns = [
    # -------------------------------------------------------------------------
    # 1. LIST FUNCTION
    # -------------------------------------------------------------------------
    path(
        "menu_item_roles/list/ui/",
        menu_views.MenuItemRoleListView.as_view(),
        name="menu_item_role_list",
    ),
    # -------------------------------------------------------------------------
    # 2. CREATE FUNCTION (Split into UI Presentation and Data Persistence)
    # -------------------------------------------------------------------------
    path(
        "menu_item_roles/create/",
        menu_views.MenuItemRoleCreateView.as_view(),
        name="menu_item_role_create",
    ),
    # -------------------------------------------------------------------------
    # 3. UPDATE FUNCTION (Handles both GET for UI prep and POST for processing)
    # -------------------------------------------------------------------------
    path(
        "menu_item_roles/update/<uuid:pk>/",
        menu_views.MenuItemRoleUpdateView.as_view(),
        name="menu_item_role_update",
    ),
    # -------------------------------------------------------------------------
    # 4. DETAIL FUNCTION (Handles both GET for UI prep and POST for processing)
    # -------------------------------------------------------------------------
    path(
        "menu_item_roles/detail/<uuid:pk>/",
        menu_views.MenuItemRoleDetailView.as_view(),
        name="menu_item_role_detail",
    ),
]
