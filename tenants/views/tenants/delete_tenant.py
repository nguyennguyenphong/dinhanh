from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from tenants.models.tenants import Tenant
from tenants.policies.tenants.tenant_policy import TenantPolicy
from tenants.services.tenants.tenant_service import TenantService


class TenantDeleteView(APIView):
    """
    Enterprise API View for hard/soft purging tenant workspace units from core storage clusters.
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = TenantService()

    def delete(self, request, pk=None, *args, **kwargs):
        try:
            tenant = Tenant.objects.get(pk=pk)
        except Tenant.DoesNotExist:
            return Response(
                {"error": "Resource not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Isolation protection rule verification 
        if not TenantPolicy.can_delete(request.user, tenant):
            return Response(
                {"error": "Critical infrastructure removal requires higher access configurations."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        self.service.delete_tenant(tenant.id, requested_by_user=request.user)
        return Response(
            {"status": "Entity context successfully dropped."}, 
            status=status.HTTP_204_NO_CONTENT
        )