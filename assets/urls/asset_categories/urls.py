from django.urls import path

from assets.views import asset_categories as asset_category_views

urlpatterns = [
    # -------------------------------------------------------------------------
    # 1. LIST FUNCTION
    # -------------------------------------------------------------------------
    path(
        "asset_categories/list/ui/",
        asset_category_views.AssetCategoryListView.as_view(),
        name="asset_category_list",
    ),
    path(
        "asset_categories/list/api/",
        asset_category_views.AssetCategoryListApiView.as_view(),
        name="asset_category_list_api",
    ),
    # -------------------------------------------------------------------------
    # 2. CREATE FUNCTION (Split into UI Presentation and Data Persistence)
    # -------------------------------------------------------------------------
    path(
        "asset_categories/create/",
        asset_category_views.AssetCategoryCreateView.as_view(),
        name="asset_category_create",
    ),
    # -------------------------------------------------------------------------
    # 3. UPDATE FUNCTION (Handles both GET for UI prep and POST for processing)
    # -------------------------------------------------------------------------
    path(
        "asset_categories/update/<uuid:pk>/",
        asset_category_views.AssetCategoryUpdateView.as_view(),
        name="asset_category_update",
    ),
    # -------------------------------------------------------------------------
    # 4. DETAIL FUNCTION (Handles both GET for UI prep and POST for processing)
    # -------------------------------------------------------------------------
    path(
        "asset_categories/detail/<uuid:pk>/",
        asset_category_views.AssetCategoryDetailView.as_view(),
        name="asset_category_detail",
    ),
    # -------------------------------------------------------------------------
    # 5. DELETE FUNCTION
    # -------------------------------------------------------------------------
    path(
        "asset_categories/delete/<uuid:pk>/",
        asset_category_views.AssetCategoryDeleteView.as_view(),
        name="asset_category_delete",
    ),
]
