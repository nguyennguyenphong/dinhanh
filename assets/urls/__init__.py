from .assets.urls import urlpatterns as asset_patterns
from .asset_categories.urls import urlpatterns as asset_category_patterns

urlpatterns = [
    *asset_patterns,
    *asset_category_patterns,
]
