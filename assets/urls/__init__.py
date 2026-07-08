from assets.urls.asset_categories.urls import urlpatterns as asset_category_patterns
from assets.urls.assets.urls import urlpatterns as asset_patterns
from assets.urls.storage_units.urls import urlpatterns as storage_unit_patterns

urlpatterns = [
    *asset_patterns,
    *asset_category_patterns,
    *storage_unit_patterns,
]
