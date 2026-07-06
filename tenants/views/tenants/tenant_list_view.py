
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from core.utils.grid import DjangoGridBuilder
from tenants.application.dtos.tenants.tenant_list_query_dto import TenantListQueryDTO
from tenants.exceptions.exception import TenantDomainError
from tenants.providers import TenantProvider
from tenants.serializers.tenants.tenant_list_query_serializer import (
    TenantListQuerySerializer,
)
from tenants.serializers.tenants.tenant_response_serializer import (
    TenantResponseSerializer,
)


class TenantListView(LoginRequiredMixin, View):
    def get(self, request):

        # Instantiate DjangoGridBuilder for tenants
        grid_builder = DjangoGridBuilder(
            grid_id="tenant-grid", api_url=reverse("tenant_list_api"), page_size=50
        )

        # Add columns
        grid_builder.add_column(
            "idx", "STT", col_type="number", width=70, sortable=False, filter=False
        )
        grid_builder.add_column("code", "Mã", col_type="text", width=120)
        grid_builder.add_column("name", "Tên đơn vị", col_type="text", width=220)
        grid_builder.add_column("domain", "Tên miền", col_type="text", width=180)
        grid_builder.add_column(
            "logo_url",
            "Logo",
            col_type="image",
            width=100,
            sortable=False,
            filter=False,
        )
        grid_builder.add_column("is_active", "Trạng thái", col_type="status", width=150)
        grid_builder.add_column("plan", "Gói dịch vụ", col_type="text", width=120)
        grid_builder.add_column("max_users", "Max Users", col_type="number", width=110)
        grid_builder.add_column(
            "max_branches", "Max Branches", col_type="number", width=130
        )
        grid_builder.add_column(
            "max_vehicles", "Max Vehicles", col_type="number", width=130
        )
        grid_builder.add_column(
            "primary_color", "Màu chính", col_type="text", width=130
        )
        grid_builder.add_column(
            "default_language", "Ngôn ngữ", col_type="text", width=130
        )
        grid_builder.add_column("currency", "Tiền tệ", col_type="text", width=180)
        grid_builder.add_column("exchange_rate", "Tỉ giá", col_type="text", width=90)
        grid_builder.add_column(
            "created_at", "Ngày tạo", col_type="datetime", width=180
        )
        grid_builder.add_column(
            "updated_at", "Ngày cập nhật", col_type="datetime", width=180
        )
        grid_builder.add_column(
            "deleted_at", "Ngày xóa", col_type="datetime", width=180
        )
        grid_builder.add_column(
            "actions",
            "Thao tác",
            col_type="actions",
            width=220,
            sortable=False,
            filter=False,
            cell_renderer_params={"app": "tenants", "key": "uuid"},
        )

        context = {
            "grid_id": grid_builder.grid_id,
            "api_url": grid_builder.api_url,
            "columns_json": grid_builder.get_columns_json(),
            "options_json": grid_builder.get_options_json(),
        }
        return render(request, "pages/tenants/list.html", context)


class TenantListApiView(LoginRequiredMixin, View):
    def get(self, request):
        # Validate query parameters using DRF serializer
        serializer = TenantListQuerySerializer(data=request.GET)
        if not serializer.is_valid():
            return JsonResponse({"error": serializer.errors}, status=400)

        validated_data = serializer.validated_data

        # Parse ordering
        ordering = validated_data.get("ordering")
        if isinstance(ordering, str):
            ordering = [ordering]
        elif not ordering:
            ordering = ["-created_at"]

        # Build query DTO
        query_dto = TenantListQueryDTO(
            search=validated_data.get("search") or None,
            plan=validated_data.get("plan") or None,
            is_active=validated_data.get("is_active"),
            ordering=ordering,
            limit=validated_data.get("limit", 50),
            offset=validated_data.get("offset", 0),
        )

        try:
            tenants, total = TenantProvider.list_tenants().execute(query_dto)
        except TenantDomainError as e:
            return JsonResponse({"error": str(e)}, status=400)

        # Serialize response data
        data_serializer = TenantResponseSerializer(tenants, many=True)

        return JsonResponse({"results": data_serializer.data, "total": total})
