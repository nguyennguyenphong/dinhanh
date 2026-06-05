from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from tenants.views.tenants.list_tenant import TenantListView
from tenants.views.tenants.create_tenant import TenantCreateView
from tenants.views.tenants.update_tenant import TenantUpdateView
from tenants.views.tenants.delete_tenant import TenantDeleteView


class TenantViewSet(viewsets.ViewSet):
    """
    Unified Endpoint Broker delegating functional executions to small standalone class nodes.
    """
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        return TenantListView.as_view()(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return TenantCreateView.as_view()(request, *args, **kwargs)

    def update(self, request, pk=None, *args, **kwargs):
        return TenantUpdateView.as_view()(request, pk=pk, *args, **kwargs)

    def destroy(self, request, pk=None, *args, **kwargs):
        return TenantDeleteView.as_view()(request, pk=pk, *args, **kwargs)