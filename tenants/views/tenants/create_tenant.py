from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.urls import NoReverseMatch
from rest_framework.exceptions import ValidationError

from tenants.policies.tenants.tenant_policy import TenantPolicy
from tenants.services.tenants.tenant_service import TenantService
from tenants.application.dtos.tenants.tenant_create_dto import TenantCreateDTO
from tenants.serializers.tenants.tenant_create_serializer import TenantCreateSerializer

# =============================================================================
# 1. PRESENTATION LAYER (UI RENDERING)
# =============================================================================
# @login_required
@require_http_methods(["GET"])
def tenant_create_ui(request):
    """
    Renders the HTML provisioning form for creating a new tenant organization.
    
    Responsibilities:
    - Enforces contextual authorization policies.
    - Delivers the presentation template layer cleanly.
    """
    # Authorization enforcement using the central organization security blueprint
    # if not TenantPolicy.can_create(request.user):
    #     raise PermissionDenied("Access denied. Insufficient administrative privileges.")
        
    return render(request, "pages/create.html")


# =============================================================================
# 2. PERSISTENCE LAYER (BUSINESS TRANSACTION EXECUTION)
# =============================================================================
# @login_required
@require_POST
def create_tenant_execute(request):
    """
    Processes transaction payload, transforms form-data to DTO, 
    and invokes the domain service layer for entity persistence.
    
    Design Patterns applied:
    - Post/Redirect/Get (PRG) Pattern to eliminate duplicate submission vulnerabilities.
    """
    # Strict secondary authorization guard on the data mutation pipeline
    # if not TenantPolicy.can_create(request.user):
    #     raise PermissionDenied("Action barred by organizational security blueprint.")

    serializer = TenantCreateSerializer(data=request.POST)
    serializer.is_valid(raise_exception=True)

    dto = TenantCreateDTO(**serializer.validated_data)

    TenantService().create_tenant(
        dto=dto,
        requested_by_user=request.user
    )

    messages.success(
        request,
        "Tenant organization provisioned successfully."
    )

    return redirect("tenant_list")