# Url tenant's module
from django.urls import path

from tenants.views.list import list_tenant
from tenants.views.create import create_tenant

urlpatterns = [
    path("", list_tenant, name="tenants"),
    path("create/", create_tenant, name="create_tenants"),
]
