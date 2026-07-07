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
    path(
        "menu_items/list/api/",
        menu_views.MenuItemListApiView.as_view(),
        name="menu_items_list_api",
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
    # -------------------------------------------------------------------------
    # 5. DELETE FUNCTION (Soft delete)
    # -------------------------------------------------------------------------
    path(
        "menu_items/delete/<uuid:pk>/",
        menu_views.MenuItemDeleteView.as_view(),
        name="menu_items_delete",
    ),
    # -------------------------------------------------------------------------
    # 6. SOFT DELETE FUNCTION
    # -------------------------------------------------------------------------
    path(
        "menu_items/soft_delete/<uuid:pk>/",
        menu_views.MenuItemSoftDeleteView.as_view(),
        name="menu_item_soft_delete",
    ),
    # -------------------------------------------------------------------------
    # 7. HARD DELETE FUNCTION
    # -------------------------------------------------------------------------
    path(
        "menu_items/hard_delete/<uuid:pk>/",
        menu_views.MenuItemHardDeleteView.as_view(),
        name="menu_item_hard_delete",
    ),
]
