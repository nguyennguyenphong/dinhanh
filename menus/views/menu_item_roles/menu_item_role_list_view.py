from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from core.utils.grid import DjangoGridBuilder
from menus.application.dtos.menu_item_roles import MenuItemRoleListQueryDto
from menus.providers.menu_item_role_provider import MenuItemRoleProvider
from menus.serializers.menu_item_roles.menu_item_role_response_serializer import (
    MenuItemRoleResponseSerializer,
)


class MenuItemRoleListView(LoginRequiredMixin, View):
    """
    Handle the rendering of the menu item roles list page using DjangoGridBuilder.
    """

    def get(self, request):
        grid_builder = DjangoGridBuilder(
            grid_id="menu-item-role-grid", api_url=reverse("menu_item_role_list_api"), page_size=50
        )

        grid_builder.add_column(
            "idx", "STT", col_type="number", width=70, sortable=False, filter=False
        )
        grid_builder.add_column("menu_item_id", "ID Mục Menu (Menu Item ID)", col_type="number", width=220)
        grid_builder.add_column("role_id", "ID Vai trò (Role ID)", col_type="number", width=220)
        grid_builder.add_column(
            "actions",
            "Thao tác",
            col_type="actions",
            width=220,
            sortable=False,
            filter=False,
            cell_renderer_params={"app": "menu_item_roles", "key": "uuid"},
        )

        context = {
            "grid_id": grid_builder.grid_id,
            "api_url": grid_builder.api_url,
            "columns_json": grid_builder.get_columns_json(),
            "options_json": grid_builder.get_options_json(),
        }
        return render(request, "pages/menu_item_roles/list.html", context)


class MenuItemRoleListApiView(LoginRequiredMixin, View):
    """
    API endpoint serving datagrid requests for menu item roles list.
    """

    def get(self, request):
        if hasattr(request, "tenant") and request.tenant:
            current_tenant_id = request.tenant.id
        elif hasattr(request.user, "tenant_id") and request.user.tenant_id:
            current_tenant_id = request.user.tenant_id
        else:
            current_tenant_id = 1

        query_dto = MenuItemRoleListQueryDto(
            tenant_id=current_tenant_id,
            limit=int(request.GET.get("limit", 50)),
            offset=int(request.GET.get("offset", 0)),
        )

        try:
            items, total = MenuItemRoleProvider.list_menu_item_roles().execute(query_dto)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

        serializer = MenuItemRoleResponseSerializer(items, many=True)
        return JsonResponse({"results": serializer.data, "total": total})
