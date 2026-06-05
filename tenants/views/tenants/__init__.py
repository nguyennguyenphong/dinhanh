# Clear out all REST Framework references (ViewSet, Permissions, etc.)
# Export clean Function-Based Views for the MVT architecture

from tenants.views.tenants.list_tenant import list_tenant
from tenants.views.tenants.create_tenant import create_tenant_execute, tenant_create_ui
from tenants.views.tenants.update_tenant import TenantUpdateView
from tenants.views.tenants.delete_tenant import TenantDeleteView

__all__ = [
    "list_tenant",
    "create_tenant_execute",
    "tenant_create_ui",
    "TenantUpdateView",
    "TenantDeleteView",
]