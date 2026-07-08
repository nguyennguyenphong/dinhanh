from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from core.utils.grid import DjangoGridBuilder
from assets.providers.asset_provider import AssetProvider
from assets.serializers.storage_unit_serializer import (
    StorageUnitListQuerySerializer,
    StorageUnitSerializer,
)


class StorageUnitListView(LoginRequiredMixin, View):

    def get(self, request):
        grid_builder = DjangoGridBuilder(
            grid_id="storage-unit-grid",
            api_url=reverse("storage_unit_list_api"),
            page_size=50,
        )

        grid_builder.add_column(
            "idx", "STT", col_type="number", width=70, sortable=False, filter=False
        )
        grid_builder.add_column("code", "Mã kho bãi", col_type="text", width=140)
        grid_builder.add_column("name", "Tên kho bãi", col_type="text", width=220)
        grid_builder.add_column("description", "Mô tả", col_type="text", width=300)
        grid_builder.add_column(
            "actions",
            "Thao tác",
            col_type="actions",
            width=180,
            sortable=False,
            filter=False,
            cell_renderer_params={"app": "storage_units", "key": "uuid"},
        )

        context = {
            "grid_id": grid_builder.grid_id,
            "api_url": grid_builder.api_url,
            "columns_json": grid_builder.get_columns_json(),
            "options_json": grid_builder.get_options_json(),
        }
        return render(request, "pages/storage_units/list.html", context)


class StorageUnitListApiView(LoginRequiredMixin, View):

    def get(self, request):
        serializer = StorageUnitListQuerySerializer(data=request.GET)
        if not serializer.is_valid():
            return JsonResponse({"error": serializer.errors}, status=400)

        validated_data = serializer.validated_data

        storage_units, total = AssetProvider.list_storage_units().execute(
            tenant_id=request.user.tenant_id if hasattr(request.user, "tenant_id") else 1,
            search=validated_data.get("search") or None,
            limit=validated_data.get("limit", 50),
            offset=validated_data.get("offset", 0),
        )

        data_serializer = StorageUnitSerializer(storage_units, many=True)
        return JsonResponse({"results": data_serializer.data, "total": total})
