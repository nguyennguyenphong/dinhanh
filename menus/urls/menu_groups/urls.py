from django.urls import path

from menus.views import menu_groups as menu_views

urlpatterns = [
    # -------------------------------------------------------------------------
    # 1. LIST FUNCTION
    # -------------------------------------------------------------------------
    path("menu_groups/list/ui/", menu_views.MenuGroupListView.as_view(), name="menu_group_list"),
    # -------------------------------------------------------------------------
    # 2. CREATE FUNCTION (Split into UI Presentation and Data Persistence)
    # -------------------------------------------------------------------------
    path("menu_groups/create/", menu_views.MenuGroupCreateView.as_view(), name="menu_group_create"),
    
]
