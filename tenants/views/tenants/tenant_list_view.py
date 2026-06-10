from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from tenants.application.dtos import TenantListQueryDTO
from tenants.exceptions.exception import TenantDomainError
from tenants.providers import TenantProvider
from tenants.views.forms import TenantFilterForm 


class TenantListView(LoginRequiredMixin, View):
    """
    Handle the rendering of the tenant list page.
    Follows MVT pattern:
    1. Extract filters from request.GET via TenantFilterForm
    2. Execute Service/Provider logic
    3. Render the template with the provided context
    """

    def get(self, request):
        form = TenantFilterForm(request.GET or None)

        search_value = request.GET.get("search_tenant", "")
        plan_value = request.GET.get("plan")
        status_value = request.GET.get("status")
        
        if form.is_valid():
            search_value = form.cleaned_data.get("search_tenant")
            plan_value = form.cleaned_data.get("plan")
            status_value = form.cleaned_data.get("status")
            # sort_by_value = form.cleaned_data.get("sort_by")
            # created_at_value = form.cleaned_data.get("created_at")

        is_active = None
        if status_value == "True":
            is_active = True
        elif status_value == "False":
            is_active = False

        if plan_value == "all":
            plan_value = None

        query_dto = TenantListQueryDTO(
            search=search_value,
            plan=plan_value,
            is_active=is_active,
            limit=int(request.GET.get("limit", 10)),
            offset=int(request.GET.get("offset", 0)),
        )

        try:
            tenants, total = TenantProvider.list_tenants().execute(query_dto)
        except TenantDomainError as e:
            return render(request, "pages/list.html", {"error": str(e), "form": form})

        context = {
            "tenants": tenants,
            "total": total,
            "query": query_dto,
            "form": form,
        }
        return render(request, "pages/list.html", context)