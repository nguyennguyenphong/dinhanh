from django.urls import path

from assets.views import assets as asset_views

urlpatterns = [
    # -------------------------------------------------------------------------
    # 1. LIST FUNCTION
    # -------------------------------------------------------------------------
    path(
        "assets/list/ui/",
        asset_views.AssetListView.as_view(),
        name="asset_list",
    ),
    path(
        "assets/list/api/",
        asset_views.AssetListApiView.as_view(),
        name="asset_list_api",
    ),
    # -------------------------------------------------------------------------
    # 2. CREATE FUNCTION (Split into UI Presentation and Data Persistence)
    # -------------------------------------------------------------------------
    path(
        "assets/create/",
        asset_views.AssetCreateView.as_view(),
        name="asset_create",
    ),
    # -------------------------------------------------------------------------
    # 3. UPDATE FUNCTION (Handles both GET for UI prep and POST for processing)
    # -------------------------------------------------------------------------
    path(
        "assets/update/<int:pk>/",
        asset_views.AssetUpdateView.as_view(),
        name="asset_update",
    ),
    # -------------------------------------------------------------------------
    # 4. DETAIL FUNCTION (Handles both GET for UI prep and POST for processing)
    # -------------------------------------------------------------------------
    path(
        "assets/detail/<int:pk>/",
        asset_views.AssetDetailView.as_view(),
        name="asset_detail",
    ),
    # -------------------------------------------------------------------------
    # 5. DELETE FUNCTION (Soft / Hard Delete API / View)
    # -------------------------------------------------------------------------
    path(
        "assets/soft_delete/<int:pk>/",
        asset_views.AssetSoftDeleteView.as_view(),
        name="asset_soft_delete",
    ),
    path(
        "assets/hard_delete/<int:pk>/",
        asset_views.AssetHardDeleteView.as_view(),
        name="asset_hard_delete",
    ),
]
