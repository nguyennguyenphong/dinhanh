from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from core.utils.grid import DjangoGridBuilder
from branches.providers.branch_provider import BranchProvider
from branches.serializers.branch_serializer import (
    BranchListQuerySerializer,
    BranchSerializer,
)


class BranchListView(LoginRequiredMixin, View):

    def get(self, request):
        grid_builder = DjangoGridBuilder(
            grid_id="branch-grid",
            api_url=reverse("branch_list_api"),
            page_size=50,
        )

        grid_builder.add_column(
            "idx", "STT", col_type="number", width=70, sortable=False, filter=False
        )
        grid_builder.add_column("code", "Mã chi nhánh", col_type="text", width=130)
        grid_builder.add_column("name", "Tên chi nhánh", col_type="text", width=250)
        grid_builder.add_column("address", "Địa chỉ", col_type="text", width=280)
        grid_builder.add_column("phone", "Số điện thoại", col_type="text", width=130)
        grid_builder.add_column("email", "Email liên hệ", col_type="text", width=180)
        grid_builder.add_column("is_active", "Trạng thái", col_type="boolean", width=120)
        grid_builder.add_column(
            "actions",
            "Thao tác",
            col_type="actions",
            width=180,
            sortable=False,
            filter=False,
            cell_renderer_params={"app": "branches", "key": "id"},
        )

        context = {
            "grid_id": grid_builder.grid_id,
            "api_url": grid_builder.api_url,
            "columns_json": grid_builder.get_columns_json(),
            "options_json": grid_builder.get_options_json(),
        }
        return render(request, "pages/branches/list.html", context)


class BranchListApiView(LoginRequiredMixin, View):

    def get(self, request):
        serializer = BranchListQuerySerializer(data=request.GET)
        if not serializer.is_valid():
            return JsonResponse({"error": serializer.errors}, status=400)

        validated_data = serializer.validated_data

        branches, total = BranchProvider.list_branches().execute(
            tenant_id=request.user.tenant_id if hasattr(request.user, "tenant_id") else 1,
            search=validated_data.get("search") or None,
            limit=validated_data.get("limit", 50),
            offset=validated_data.get("offset", 0),
        )

        data_serializer = BranchSerializer(branches, many=True)
        return JsonResponse({"results": data_serializer.data, "total": total})
