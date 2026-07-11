from assets.views.assets.asset_create_view import AssetCreateView
from assets.views.assets.asset_detail_view import AssetDetailView
from assets.views.assets.asset_hard_delete_view import AssetHardDeleteView
from assets.views.assets.asset_list_view import AssetListApiView, AssetListView
from assets.views.assets.asset_soft_delete_view import AssetSoftDeleteView
from assets.views.assets.asset_update_view import AssetUpdateView

__all__ = [
    "AssetCreateView",
    "AssetSoftDeleteView",
    "AssetHardDeleteView",
    "AssetDetailView",
    "AssetListView",
    "AssetListApiView",
    "AssetUpdateView",
]
