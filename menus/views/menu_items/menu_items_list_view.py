from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from menus.application.dtos.menu_items import MenuItemListQueryDto
from menus.exceptions import MenuItemDomainError
from menus.providers.menu_item_provider import MenuItemProvider


class MenuItemListView(LoginRequiredMixin, View):
    """
    Handle the rendering of the menu list page.
    Follows MVT pattern:
    1. Extract filters from request.GET
    2. Execute Service/Provider logic
    3. Render the template with the provided context
    """

    def get(self, request):
        search_value = request.GET.get("search", "")
        sort_value = request.GET.get("sort_by", "")
        status_value = request.GET.get("status")
        group_id_value = request.GET.get("group_id")
        parent_id_value = request.GET.get("parent_id")
        sort_by = []

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

        group_id = (
            int(group_id_value) if group_id_value and group_id_value.isdigit() else None
        )
        parent_id = (
            int(parent_id_value)
            if parent_id_value and parent_id_value.isdigit()
            else None
        )

        query_dto = MenuItemListQueryDto(
            tenant_id=current_tenant_id,
            group_id=group_id,
            parent_id=parent_id,
            search=search_value,
            is_active=is_active,
            ordering=sort_by,
            limit=int(request.GET.get("limit", 10)),
            offset=int(request.GET.get("offset", 0)),
        )

        try:
            menu_items, total = MenuItemProvider.list_menu_items().execute(query_dto)
        except MenuItemDomainError as e:
            return render(request, "pages/menu_items/list.html", {"error": str(e)})

        context = {
            "menu_items": menu_items,
            "total": total,
            "query": query_dto,
        }

        return render(request, "pages/menu_items/list.html", context)
