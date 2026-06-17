from django.urls import path

from menus.views import menu_groups as menu_views

urlpatterns = [
    # -------------------------------------------------------------------------
    # 1. LIST FUNCTION
    # -------------------------------------------------------------------------
    path(
        "menu_groups/list/ui/",
        menu_views.MenuGroupListView.as_view(),
        name="menu_group_list",
    ),
    # -------------------------------------------------------------------------
    # 2. CREATE FUNCTION (Split into UI Presentation and Data Persistence)
    # -------------------------------------------------------------------------
    path(
        "menu_groups/create/",
        menu_views.MenuGroupCreateView.as_view(),
        name="menu_group_create",
    ),
    # -------------------------------------------------------------------------
    # 3. UPDATE FUNCTION (Handles both GET for UI prep and POST for processing)
    # -------------------------------------------------------------------------
    path(
        "menu_groups/update/<uuid:pk>/",
        menu_views.MenuGroupUpdateView.as_view(),
        name="menu_group_update",
    ),
    # -------------------------------------------------------------------------
    # 4. DETAIL FUNCTION (Handles both GET for UI prep and POST for processing)
    # -------------------------------------------------------------------------
    path(
        "menu_groups/detail/<uuid:pk>/",
        menu_views.MenuGroupDetailView.as_view(),
        name="menu_group_detail",
    ),
]
