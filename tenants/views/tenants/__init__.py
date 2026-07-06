# Clear out all REST Framework references (ViewSet, Permissions, etc.)
# Export clean Function-Based Views for the MVT architecture

from tenants.views.tenants.tenant_create_view import TenantCreateView
from tenants.views.tenants.tenant_detail_view import TenantDetailView
from tenants.views.tenants.tenant_hard_delete_view import TenantHardDeleteView
from tenants.views.tenants.tenant_list_view import TenantListApiView, TenantListView
from tenants.views.tenants.tenant_soft_delete_view import TenantSoftDeleteView
from tenants.views.tenants.tenant_update_view import TenantUpdateView

__all__ = [
    "TenantCreateView",
    "TenantDetailView",
    "TenantHardDeleteView",
    "TenantListView",
    "TenantListApiView",
    "TenantSoftDeleteView",
    "TenantUpdateView",
]
