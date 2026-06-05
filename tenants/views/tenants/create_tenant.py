from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from tenants.serializers.tenants.tenant_serializer import TenantSerializer
from tenants.policies.tenants.tenant_policy import TenantPolicy
from tenants.services.tenants.tenant_service import TenantService
from tenants.dtos.tenants.tenant_create_dto import TenantCreateDTO

@login_required
def tenant_create_ui(request):
    """
    MVT View: Renders the HTML form page for creating a new tenant.
    """
    # Authorization check using the dedicated policy layer
    if not TenantPolicy.can_create(request.user):
        raise PermissionDenied("You do not have permission to access this page.")
        
    return render(request, "pages/create.html")

class TenantCreateView(APIView):
    """
    Enterprise API View for provisioning new tenant accounts.
    """
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = TenantService()

    def post(self, request, *args, **kwargs):
        # Strict organizational access control rule mapping
        if not TenantPolicy.can_create(request.user):
            return Response(
                {"error": "Action barred by organizational security blueprint."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Explicit data transfer contract translation layer
        dto = TenantCreateDTO(
            code=request.data.get("code"),
            name=request.data.get("name"),
            domain=request.data.get("domain"),
            logo_url=request.data.get("logo_url"),
            primary_color=request.data.get("primary_color", "#3B82F6"),
            plan=request.data.get("plan", "STANDARD"),
            currency=request.data.get("currency", "VND"),
            exchange_rate=float(request.data.get("exchange_rate", 1.0000)),
            default_language=request.data.get("default_language", "vi"),
            timezone=request.data.get("timezone", "Asia/Ho_Chi_Minh"),
            settings=request.data.get("settings", {}),
            max_users=int(request.data.get("max_users", 10)),
            max_branches=int(request.data.get("max_branches", 1)),
            max_vehicles=int(request.data.get("max_vehicles", 50))
        )

        tenant = self.service.create_tenant(dto, requested_by_user=request.user)
        return Response(TenantSerializer(tenant).data, status=status.HTTP_201_CREATED)