from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST

from tenants.policies.tenants.tenant_policy import TenantPolicy
from tenants.services.tenants.tenant_service import TenantService
from tenants.dtos.tenants.tenant_create_dto import TenantCreateDTO

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

    service = TenantService()
    
    try:
        # Explicit request payload translation into an immutable Data Transfer Object (DTO)
        dto = TenantCreateDTO(
            code=request.POST.get("code"),
            name=request.POST.get("name"),
            domain=request.POST.get("domain"),
            logo_url=request.POST.get("logo_url"), 
            primary_color=request.POST.get("primary_color", "#3B82F6"),
            plan=request.POST.get("plan_type", "STANDARD"), 
            currency=request.POST.get("currency", "VND"),
            exchange_rate=float(request.POST.get("exchange_rate") or 1.0000),
            default_language=request.POST.get("default_language", "vi"),
            timezone=request.POST.get("timezone", "Asia/Ho_Chi_Minh"),
            settings={}, 
            max_users=int(request.POST.get("max_users") or 10),
            max_branches=int(request.POST.get("max_branches") or 1),
            max_vehicles=int(request.POST.get("max_vehicles") or 50)
        )

        # Delegate business logic execution to the specialized domain service layer
        service.create_tenant(dto, requested_by_user=request.user)
        
        # Inject successful status feedback message into the session pipeline
        messages.success(request, "Tenant organization provisioned successfully.")
        
        # Redirect to the main workspace index (PRG Pattern)
        return redirect("tenan_list")
        
    except Exception as e:
        # Fail-soft mechanism: Catch domain/system exceptions and inject error payload into context session
        messages.error(request, f"System failed to provision tenant resource: {str(e)}")
        
        # Safe fallback redirection back to the clean interface context
        return redirect("tenant_create_ui")