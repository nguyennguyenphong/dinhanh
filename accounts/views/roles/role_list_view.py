from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from accounts.models import Role
from accounts.serializers.role_serializer import (
    RoleListQuerySerializer,
    RoleSerializer,
)
from core.utils.grid import DjangoGridBuilder


class RoleListView(LoginRequiredMixin, View):

    def get(self, request):
        grid_builder = DjangoGridBuilder(
            grid_id="role-grid",
            api_url=reverse("role_list_api"),
            page_size=50,
        )

        grid_builder.add_column(
            "idx", "STT", col_type="number", width=70, sortable=False, filter=False
        )
        grid_builder.add_column("name", "Tên vai trò", col_type="text", width=200)
        grid_builder.add_column("slug", "Mã vai trò (Slug)", col_type="text", width=150)
        grid_builder.add_column("description", "Mô tả", col_type="text", width=300)
        grid_builder.add_column("is_system", "Hệ thống", col_type="boolean", width=120)
        grid_builder.add_column(
            "is_active", "Trạng thái", col_type="boolean", width=120
        )
        grid_builder.add_column(
            "actions",
            "Thao tác",
            col_type="actions",
            width=180,
            sortable=False,
            filter=False,
            cell_renderer_params={"app": "roles", "key": "id"},
        )

        context = {
            "grid_id": grid_builder.grid_id,
            "api_url": grid_builder.api_url,
            "columns_json": grid_builder.get_columns_json(),
            "options_json": grid_builder.get_options_json(),
        }
        return render(request, "pages/roles/list.html", context)


class RoleListApiView(LoginRequiredMixin, View):

    def get(self, request):
        serializer = RoleListQuerySerializer(data=request.GET)
        if not serializer.is_valid():
            return JsonResponse({"error": serializer.errors}, status=400)

        validated_data = serializer.validated_data
        search = validated_data.get("search")
        limit = validated_data.get("limit", 50)
        offset = validated_data.get("offset", 0)

        tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else 1

        from accounts.application.dtos.roles.role_list_query_dto import RoleListQueryDto
        from accounts.providers.role_provider import RoleProvider

        query_dto = RoleListQueryDto(
            tenant_id=tenant_id,
            search=search,
            limit=limit,
            offset=offset,
        )

        roles_dtos, total = RoleProvider.list_roles().execute(query_dto)

        data_serializer = RoleSerializer(roles_dtos, many=True)
        return JsonResponse({"results": data_serializer.data, "total": total})
