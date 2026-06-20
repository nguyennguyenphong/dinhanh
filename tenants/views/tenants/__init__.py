# Clear out all REST Framework references (ViewSet, Permissions, etc.)
# Export clean Function-Based Views for the MVT architecture

from .tenant_create_view import TenantCreateView
from .tenant_detail_view import TenantDetailView
from .tenant_hard_delete_view import TenantHardDeleteView
from .tenant_list_view import TenantListApiView, TenantListView
from .tenant_soft_delete_view import TenantSoftDeleteView
from .tenant_update_view import TenantUpdateView

__all__ = [
    "TenantCreateView",
    "TenantDetailView",
    "TenantHardDeleteView",
    "TenantListView",
    "TenantListApiView",
    "TenantSoftDeleteView",
    "TenantUpdateView",
]
