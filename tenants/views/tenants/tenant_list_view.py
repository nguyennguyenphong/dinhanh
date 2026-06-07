from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from tenants.application.dtos import TenantListQueryDTO
from tenants.providers import TenantProvider
from tenants.exceptions.exception import TenantDomainError

class TenantListView(LoginRequiredMixin, View):
    """
    Handle the rendering of the tenant list page.
    Follows MVT pattern:
    1. Extract filters from request.GET
    2. Execute Service/Provider logic
    3. Render the template with the provided context
    """
    
    def get(self, request):
        active_param = request.GET.get("is_active")

        is_active = None
        if active_param == "true":
            is_active = True
        elif active_param == "false":
            is_active = False
            
        # Extract query parameters for filtering/pagination
        query_dto = TenantListQueryDTO(
            search=request.GET.get("search"),
            plan=request.GET.get("plan"),
            is_active=is_active,
            limit=int(request.GET.get("limit", 10)),
            offset=int(request.GET.get("offset", 0)),
        )

        try:
            # Execute business logic via Provider
            tenants, total = TenantProvider.list_tenants().execute(query_dto)
        except TenantDomainError as e:
            # Handle domain-specific errors (e.g., render error page or show message)
            return render(request, 'pages/list.html', {'error': str(e)})

        # Render the template with data
        context = {
            'tenants': tenants,
            'total': total,
            'query': query_dto
        }
        return render(request, 'pages/list.html', context)