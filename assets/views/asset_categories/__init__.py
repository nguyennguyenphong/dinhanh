from assets.views.asset_categories.asset_category_create_view import (
    AssetCategoryCreateView,
)
from assets.views.asset_categories.asset_category_detail_view import (
    AssetCategoryDetailView,
)
from assets.views.asset_categories.asset_category_hard_delete_view import (
    AssetCategoryHardDeleteView,
)
from assets.views.asset_categories.asset_category_list_view import (
    AssetCategoryListApiView,
    AssetCategoryListView,
)
from assets.views.asset_categories.asset_category_soft_delete_view import (
    AssetCategorySoftDeleteView,
)
from assets.views.asset_categories.asset_category_update_view import (
    AssetCategoryUpdateView,
)

__all__ = [
    "AssetCategoryCreateView",
    "AssetCategorySoftDeleteView",
    "AssetCategoryHardDeleteView",
    "AssetCategoryDetailView",
    "AssetCategoryListView",
    "AssetCategoryListApiView",
    "AssetCategoryUpdateView",
]
