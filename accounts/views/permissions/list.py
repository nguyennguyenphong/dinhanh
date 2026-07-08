from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from accounts.models import Permission
from accounts.serializers.permission_serializer import (
    PermissionListQuerySerializer,
    PermissionSerializer,
)
from core.utils.grid import DjangoGridBuilder


class PermissionListView(LoginRequiredMixin, View):

    def get(self, request):
        grid_builder = DjangoGridBuilder(
            grid_id="permission-grid",
            api_url=reverse("permission_list_api"),
            page_size=50,
        )

        grid_builder.add_column(
            "idx", "STT", col_type="number", width=70, sortable=False, filter=False
        )
        grid_builder.add_column(
            "codename", "Mã quyền (Codename)", col_type="text", width=180
        )
        grid_builder.add_column("name", "Tên quyền", col_type="text", width=220)
        grid_builder.add_column("module", "Module", col_type="text", width=130)
        grid_builder.add_column(
            "action", "Hành động (Action)", col_type="text", width=120
        )
        grid_builder.add_column("description", "Mô tả", col_type="text", width=280)
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
            cell_renderer_params={"app": "permissions", "key": "id"},
        )

        context = {
            "grid_id": grid_builder.grid_id,
            "api_url": grid_builder.api_url,
            "columns_json": grid_builder.get_columns_json(),
            "options_json": grid_builder.get_options_json(),
        }
        return render(request, "pages/permission_list.html", context)


class PermissionListApiView(LoginRequiredMixin, View):

    def get(self, request):
        serializer = PermissionListQuerySerializer(data=request.GET)
        if not serializer.is_valid():
            return JsonResponse({"error": serializer.errors}, status=400)

        validated_data = serializer.validated_data
        search = validated_data.get("search")
        limit = validated_data.get("limit", 50)
        offset = validated_data.get("offset", 0)

        tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else 1
        queryset = Permission.objects.filter(tenant_id=tenant_id)

        if search:
            queryset = queryset.filter(
                Q(codename__icontains=search)
                | Q(name__icontains=search)
                | Q(module__icontains=search)
            )

        total = queryset.count()
        permissions = queryset.order_by("codename")[offset : offset + limit]

        data_serializer = PermissionSerializer(permissions, many=True)
        return JsonResponse({"results": data_serializer.data, "total": total})
