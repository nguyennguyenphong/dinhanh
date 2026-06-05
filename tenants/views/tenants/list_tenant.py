from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

# Import from Repository layer instead of direct ORM inside View for Enterprise abstraction
from tenants.repositories.tenants.tenant_repository import TenantRepository
from tenants.policies.tenants.tenant_policy import TenantPolicy


@login_required
def list_tenant(request):
    """
    Enterprise MVT View: Handles secure server-side rendering 
    for the tenant registry dashboard template.
    """
    
    # 1. Authorization check using the dedicated enterprise policy layer
    if not TenantPolicy.can_list(request.user):
        raise PermissionDenied("Unauthorized context access.")
        
    # 2. Fetch baseline data through the Repository (Data Access Layer)
    queryset = TenantRepository.get_all_active()
    
    # 3. High-performance filtering directly from URL GET query string parameters
    code_filter = request.GET.get('code', '').strip()
    if code_filter:
        queryset = queryset.filter(code__icontains=code_filter)
        
    # 4. Construct rendering state context payload (Pass QuerySet directly to template)
    context = {
        "tenants": queryset,
        "search_code": code_filter,
    }
    
    # 5. Return synchronous HTTP response with compiled HTML output page
    return render(request, "pages/list.html", context)