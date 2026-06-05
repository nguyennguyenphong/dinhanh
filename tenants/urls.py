# Url tenant's module
from django.urls import path

from tenants.views.tenants.list_tenant import list_tenant
from tenants.views.tenants.create_tenant import create_tenant, TenantCreateAPIView

urlpatterns = [
    path("list/", list_tenant, name="tenants"),
    path("create/", create_tenant, name="create_tenants"),
    path("create/", TenantCreateAPIView.as_view(), name="create_tenants"),
]
