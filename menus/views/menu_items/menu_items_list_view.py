from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from core.utils.grid import DjangoGridBuilder
from menus.application.dtos.menu_items import MenuItemListQueryDto
from menus.exceptions import MenuItemDomainError
from menus.providers.menu_item_provider import MenuItemProvider
from menus.serializers.menu_items.menu_item_response_serializer import (
    MenuItemResponseSerializer,
)


class MenuItemListView(LoginRequiredMixin, View):
    """
    Handle the rendering of the menu items list page using DjangoGridBuilder.
    """

    def get(self, request):
        grid_builder = DjangoGridBuilder(
            grid_id="menu-item-grid",
            api_url=reverse("menu_items_list_api"),
            page_size=50,
        )

        grid_builder.add_column(
            "idx", "STT", col_type="number", width=70, sortable=False, filter=False
        )
        grid_builder.add_column("label", "Nhãn (Label)", col_type="text", width=200)
        grid_builder.add_column("code", "Mã (Code)", col_type="text", width=180)
        grid_builder.add_column("url_path", "URL Path", col_type="text", width=220)
        grid_builder.add_column(
            "sort_order", "Thứ tự sắp xếp", col_type="number", width=130
        )
        grid_builder.add_column("is_active", "Trạng thái", col_type="status", width=150)
        grid_builder.add_column(
            "actions",
            "Thao tác",
            col_type="actions",
            width=220,
            sortable=False,
            filter=False,
            cell_renderer_params={"app": "menu_items", "key": "uuid"},
        )

        context = {
            "grid_id": grid_builder.grid_id,
            "api_url": grid_builder.api_url,
            "columns_json": grid_builder.get_columns_json(),
            "options_json": grid_builder.get_options_json(),
        }
        return render(request, "pages/menu_items/list.html", context)


class MenuItemListApiView(LoginRequiredMixin, View):
    """
    API endpoint serving datagrid requests for menu items list.
    """

    def get(self, request):
        search_value = request.GET.get("search") or ""
        sort_value = request.GET.get("sort_by") or ""
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
        else:
            sort_by = ["-created_at"]

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
            limit=int(request.GET.get("limit", 50)),
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
