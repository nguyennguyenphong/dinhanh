from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from menus.application.dtos import MenuGroupListQueryDto
from menus.exceptions import MenuGroupDomainError
from menus.providers import MenuGroupProvider
from menus.views.forms import MenuGroupFilterForm


class MenuGroupListView(LoginRequiredMixin, View):
    """
    Handle the rendering of the menu list page.
    Follows MVT pattern:
    1. Extract filters from request.GET via MenuFilterForm
    2. Execute Service/Provider logic
    3. Render the template with the provided context
    """

    def get(self, request):
        form = MenuGroupFilterForm(request.GET or None)

        search_value = request.GET.get("search_menu_group", "")
        sort_value = request.GET.get("sort_by", "")
        status_value = request.GET.get("status")
        sort_by = []

        if form.is_valid():
            search_value = form.cleaned_data.get("search_menu_group")
            sort_value = form.cleaned_data.get("sort_by")
            status_value = form.cleaned_data.get("status")

        is_active = None
        if status_value == "True":
            is_active = True
        elif status_value == "False":
            is_active = False

        if sort_value:
            sort_by = [sort_value]

        if hasattr(request, "tenant") and request.tenant:
            current_tenant_id = request.tenant.id
        elif hasattr(request.user, "tenant_id") and request.user.tenant_id:
            current_tenant_id = request.user.tenant_id
        else:
            current_tenant_id = 1

        query_dto = MenuGroupListQueryDto(
            tenant_id=current_tenant_id,
            search=search_value,
            is_active=is_active,
            ordering=sort_by,
            limit=int(request.GET.get("limit", 10)),
            offset=int(request.GET.get("offset", 0)),
        )

        try:
            menu_groups, total = MenuGroupProvider.list_menu_groups().execute(query_dto)
        except MenuGroupDomainError as e:
            return render(
                request, "pages/menu_groups/list.html", {"error": str(e), "form": form}
            )

        context = {
            "menu_groups": menu_groups,
            "total": total,
            "query": query_dto,
            "form": form,
        }

        return render(request, "pages/menu_groups/list.html", context)
