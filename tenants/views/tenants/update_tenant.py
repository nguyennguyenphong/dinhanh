from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from tenants.models.tenants import Tenant
from tenants.serializers.tenants.tenant_serializer import TenantSerializer
from tenants.policies.tenants.tenant_policy import TenantPolicy
from tenants.services.tenants.tenant_service import TenantService
from tenants.dtos.tenants.tenant_update_dto import TenantUpdateDTO


class TenantUpdateView(APIView):
    """
    Enterprise API View for updating mutations on a specific Tenant resource.
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = TenantService()

    def put(self, request, pk=None, *args, **kwargs):
        try:
            tenant = Tenant.objects.get(pk=pk)
        except Tenant.DoesNotExist:
            return Response(
                {"error": "Target entity object absent."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Domain boundaries ownership structure control validation
        if not TenantPolicy.can_update(request.user, tenant):
            return Response(
                {"error": "Operation denied by current state constraints."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # Dynamic construction mapping to avoid dirty updates on optional properties
        dto = TenantUpdateDTO(
            name=request.data.get("name"),
            domain=request.data.get("domain"),
            logo_url=request.data.get("logo_url"),
            primary_color=request.data.get("primary_color"),
            plan=request.data.get("plan"),
            currency=request.data.get("currency"),
            exchange_rate=float(request.data.get("exchange_rate")) if request.data.get("exchange_rate") else None,
            default_language=request.data.get("default_language"),
            timezone=request.data.get("timezone"),
            is_active=request.data.get("is_active"),
            settings=request.data.get("settings"),
            max_users=int(request.data.get("max_users")) if request.data.get("max_users") else None,
            max_branches=int(request.data.get("max_branches")) if request.data.get("max_branches") else None,
            max_vehicles=int(request.data.get("max_vehicles")) if request.data.get("max_vehicles") else None,
        )

        updated_tenant = self.service.update_tenant(tenant.id, dto, requested_by_user=request.user)
        return Response(TenantSerializer(updated_tenant).data, status=status.HTTP_200_OK)