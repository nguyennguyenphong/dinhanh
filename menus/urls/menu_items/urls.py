from django.urls import path

from menus.views import menu_items as menu_views

urlpatterns = [
    # -------------------------------------------------------------------------
    # 1. LIST FUNCTION
    # -------------------------------------------------------------------------
    path(
        "menu_items/list/ui/",
        menu_views.MenuItemListView.as_view(),
        name="menu_items_list",
    ),
    # -------------------------------------------------------------------------
    # 2. CREATE FUNCTION (Split into UI Presentation and Data Persistence)
    # -------------------------------------------------------------------------
    path(
        "menu_items/create/",
        menu_views.MenuItemCreateView.as_view(),
        name="menu_items_create",
    ),
    # -------------------------------------------------------------------------
    # 3. UPDATE FUNCTION (Handles both GET for UI prep and POST for processing)
    # -------------------------------------------------------------------------
    path(
        "menu_items/update/<uuid:pk>/",
        menu_views.MenuItemUpdateView.as_view(),
        name="menu_items_update",
    ),
    # -------------------------------------------------------------------------
    # 4. DETAIL FUNCTION (Handles both GET for UI prep and POST for processing)
    # -------------------------------------------------------------------------
    path(
        "menu_items/detail/<uuid:pk>/",
        menu_views.MenuItemDetailView.as_view(),
        name="menu_items_detail",
    ),
]
