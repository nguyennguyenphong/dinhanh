from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from core.utils.grid import DjangoGridBuilder
from menus.application.dtos import MenuGroupListQueryDto
from menus.exceptions import MenuGroupDomainError
from menus.providers import MenuGroupProvider
from menus.serializers.menu_groups.menu_group_response_serializer import (
    MenuGroupResponseSerializer,
)


class MenuGroupListView(LoginRequiredMixin, View):
    """
    Handle the rendering of the menu groups list page using DjangoGridBuilder.
    """

    def get(self, request):
        grid_builder = DjangoGridBuilder(
            grid_id="menu-group-grid", api_url=reverse("menu_group_list_api"), page_size=50
        )

        grid_builder.add_column(
            "idx", "STT", col_type="number", width=70, sortable=False, filter=False
        )
        grid_builder.add_column("label", "Tên nhóm menu", col_type="text", width=220)
        grid_builder.add_column("code", "Mã nhóm menu", col_type="text", width=180)
        grid_builder.add_column("sort_order", "Thứ tự sắp xếp", col_type="number", width=130)
        grid_builder.add_column("is_active", "Trạng thái", col_type="status", width=150)
        grid_builder.add_column(
            "actions",
            "Thao tác",
            col_type="actions",
            width=220,
            sortable=False,
            filter=False,
            cell_renderer_params={"app": "menu_groups", "key": "uuid"},
        )

        context = {
            "grid_id": grid_builder.grid_id,
            "api_url": grid_builder.api_url,
            "columns_json": grid_builder.get_columns_json(),
            "options_json": grid_builder.get_options_json(),
        }
        return render(request, "pages/menu_groups/list.html", context)


class MenuGroupListApiView(LoginRequiredMixin, View):
    """
    API endpoint serving datagrid requests for menu groups list.
    """

    def get(self, request):
        search_value = request.GET.get("search") or ""
        sort_value = request.GET.get("sort_by") or ""
        status_value = request.GET.get("status")
        sort_by = []

        is_active = None
        if status_value == "True":
            is_active = True
        elif status_value == "False":
            is_active = False

        if sort_value:
            sort_by = [sort_value]
        else:
            sort_by = ["-created_at"]

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
            limit=int(request.GET.get("limit", 50)),
            offset=int(request.GET.get("offset", 0)),
        )

        try:
            menu_groups, total = MenuGroupProvider.list_menu_groups().execute(query_dto)
        except MenuGroupDomainError as e:
            return JsonResponse({"error": str(e)}, status=400)

        serializer = MenuGroupResponseSerializer(menu_groups, many=True)
        return JsonResponse({"results": serializer.data, "total": total})
