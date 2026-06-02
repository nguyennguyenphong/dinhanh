# Url tenant's module
from django.urls import path

from tenants.views.list import list_tenant

urlpatterns = [
    path("", list_tenant, name="tenants"),
]
