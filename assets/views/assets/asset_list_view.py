from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from assets.providers.asset_provider import AssetProvider
from assets.serializers.asset_list_query_serializer import AssetListQuerySerializer
from assets.serializers.asset_response_serializer import AssetResponseSerializer
from core.utils.grid import DjangoGridBuilder


class AssetListView(LoginRequiredMixin, View):

    def get(self, request):
        grid_builder = DjangoGridBuilder(
            grid_id="asset-grid", api_url=reverse("asset_list_api"), page_size=50
        )

        grid_builder.add_column(
            "idx", "STT", col_type="number", width=70, sortable=False, filter=False
        )
        grid_builder.add_column("code", "Mã tài sản", col_type="text", width=140)
        grid_builder.add_column("name", "Tên tài sản", col_type="text", width=220)
        grid_builder.add_column("serial_number", "Số sê-ri", col_type="text", width=130)
        grid_builder.add_column("purchase_date", "Ngày mua", col_type="date", width=130)
        grid_builder.add_column(
            "purchase_price", "Nguyên giá", col_type="number", width=140
        )
        grid_builder.add_column(
            "depreciation_rate", "Tỷ lệ khấu hao (%)", col_type="number", width=140
        )
        grid_builder.add_column(
            "current_value", "Giá trị còn lại", col_type="number", width=140
        )
        grid_builder.add_column("status", "Trạng thái", col_type="status", width=130)
        grid_builder.add_column(
            "actions",
            "Thao tác",
            col_type="actions",
            width=180,
            sortable=False,
            filter=False,
            cell_renderer_params={"app": "assets", "key": "id"},
        )

        context = {
            "grid_id": grid_builder.grid_id,
            "api_url": grid_builder.api_url,
            "columns_json": grid_builder.get_columns_json(),
            "options_json": grid_builder.get_options_json(),
        }
        return render(request, "pages/assets/list.html", context)


class AssetListApiView(LoginRequiredMixin, View):

    def get(self, request):
        serializer = AssetListQuerySerializer(data=request.GET)
        if not serializer.is_valid():
            return JsonResponse({"error": serializer.errors}, status=400)

        validated_data = serializer.validated_data

        ordering = validated_data.get("ordering")
        if isinstance(ordering, str):
            ordering = [ordering]
        elif not ordering:
            ordering = ["-created_at"]

        filters = {}
        if validated_data.get("status"):
            filters["status"] = validated_data.get("status")
        if validated_data.get("category_id"):
            filters["category_id"] = validated_data.get("category_id")
        if validated_data.get("branch_id"):
            filters["branch_id"] = validated_data.get("branch_id")

        assets, total = AssetProvider.list_assets().execute(
            tenant_id=(
                request.user.tenant_id if hasattr(request.user, "tenant_id") else 1
            ),
            filters=filters,
            search=validated_data.get("search") or None,
            ordering=ordering,
            limit=validated_data.get("limit", 50),
            offset=validated_data.get("offset", 0),
        )

        data_serializer = AssetResponseSerializer(assets, many=True)
        return JsonResponse({"results": data_serializer.data, "total": total})
