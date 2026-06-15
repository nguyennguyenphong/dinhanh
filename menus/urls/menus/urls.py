from django.urls import path

from menus.views import menus as menu_views

urlpatterns = [
    # -------------------------------------------------------------------------
    # 1. LIST FUNCTION
    # -------------------------------------------------------------------------
    path("list/ui/", menu_views.MenuListView.as_view(), name="menu_list"),
    # -------------------------------------------------------------------------
    # 2. CREATE FUNCTION (Split into UI Presentation and Data Persistence)
    # -------------------------------------------------------------------------
    path("create/", menu_views.MenuCreateView.as_view(), name="menu_create"),
    
]
