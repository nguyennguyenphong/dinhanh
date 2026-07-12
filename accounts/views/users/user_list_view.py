from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from accounts.models import UserAccount
from accounts.serializers.user_serializer import (
    UserListQuerySerializer,
    UserSerializer,
)
from core.utils.grid import DjangoGridBuilder


class UserListView(LoginRequiredMixin, View):

    def get(self, request):
        grid_builder = DjangoGridBuilder(
            grid_id="user-grid",
            api_url=reverse("user_list_api"),
            page_size=50,
        )

        grid_builder.add_column(
            "idx", "STT", col_type="number", width=70, sortable=False, filter=False
        )
        grid_builder.add_column("username", "Tên đăng nhập", col_type="text", width=150)
        grid_builder.add_column("email", "Email", col_type="text", width=200)
        grid_builder.add_column("full_name", "Họ và tên", col_type="text", width=200)
        grid_builder.add_column("phone", "Số điện thoại", col_type="text", width=130)
        grid_builder.add_column("tenant_name", "Doanh nghiệp", col_type="text", width=180)
        grid_builder.add_column("branch_name", "Chi nhánh", col_type="text", width=150)
        grid_builder.add_column(
            "must_change_password", "Yêu cầu đổi MK", col_type="boolean", width=140
        )
        grid_builder.add_column(
            "password_expires_at", "Hết hạn mật khẩu", col_type="datetime", width=160
        )
        grid_builder.add_column(
            "locked_until", "Khóa tài khoản đến", col_type="datetime", width=160
        )
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
            cell_renderer_params={"app": "users", "key": "id"},
        )

        context = {
            "grid_id": grid_builder.grid_id,
            "api_url": grid_builder.api_url,
            "columns_json": grid_builder.get_columns_json(),
            "options_json": grid_builder.get_options_json(),
        }
        return render(request, "pages/users/list.html", context)


class UserListApiView(LoginRequiredMixin, View):

    def get(self, request):
        serializer = UserListQuerySerializer(data=request.GET)
        if not serializer.is_valid():
            return JsonResponse({"error": serializer.errors}, status=400)

        validated_data = serializer.validated_data
        search = validated_data.get("search")
        limit = validated_data.get("limit", 50)
        offset = validated_data.get("offset", 0)

        tenant_id = request.user.tenant_id if hasattr(request.user, "tenant_id") else 1

        from accounts.application.dtos.users.user_list_query_dto import UserListQueryDto
        from accounts.providers.user_provider import UserProvider

        query_dto = UserListQueryDto(
            tenant_id=tenant_id,
            search=search,
            limit=limit,
            offset=offset,
        )

        users_dtos, total = UserProvider.list_users().execute(query_dto)

        data_serializer = UserSerializer(users_dtos, many=True)
        return JsonResponse({"results": data_serializer.data, "total": total})
