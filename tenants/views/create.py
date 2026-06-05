# ============================================================================
# FILE: apps/tenants/views/tenant_view.py
# ============================================================================
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render

from tenants.policies.tenant_policy import TenantCreationPolicy
from tenants.dtos.tenant_dto import TenantCreateDTO
from tenants.services.tenant_service import TenantRegistrationService

# Show view ui 
# Method: GET
# URL: /tenants/create/
def create_tenant(request):
    return render(request, "pages/create.html")

# Handle create tenant logic 
# Method: POST
# URL: /tenants/create/
class TenantCreateAPIView(APIView):
    """
    Controller Endpoint exposed to process creation commands for new Tenants.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # 1. Evaluate authorization boundaries via Policy
        TenantCreationPolicy.is_allowed_to_create(request.user)

        # 2. Ingest payload and validate format structures via DTO
        dto = TenantCreateDTO(data=request.data)
        dto.is_valid(raise_exception=True)

        # 3. Hand off the clean data into the core Domain Service layer
        service = TenantRegistrationService()
        tenant_instance = service.execute(dto.validated_data)

        # 4. Construct high-performance standardized output payload
        return Response(
            {
                "success": True,
                "message": "Tenant successfully onboarded and resource queuing initiated.",
                "data": {
                    "id": tenant_instance.id,
                    "uuid": str(tenant_instance.uuid),
                    "code": tenant_instance.code,
                    "name": tenant_instance.name,
                    "plan": tenant_instance.plan,
                    "currency": tenant_instance.currency,
                    "timezone": tenant_instance.timezone,
                }
            },
            status=status.HTTP_201_CREATED
        )