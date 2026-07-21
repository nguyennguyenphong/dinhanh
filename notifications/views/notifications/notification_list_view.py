from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.utils.grid import DjangoGridBuilder
from notifications.application.dtos.notifications.notification_list_query_dto import (
    NotificationListQueryDTO,
)
from notifications.providers.notification_provider import NotificationProvider
from notifications.serializers.notifications.notification_list_query_serializer import (
    NotificationListQuerySerializer,
)
from notifications.serializers.notifications.notification_response_serializer import (
    NotificationResponseSerializer,
)


class NotificationListView(LoginRequiredMixin, View):

    def get(self, request):
        grid_builder = DjangoGridBuilder(
            grid_id="notification-log-grid",
            api_url=reverse("notification_log_list_api"),
            page_size=20,
        )
        grid_builder.add_column(
            "idx", "STT", col_type="number", width=70, sortable=False, filter=False
        )
        grid_builder.add_column("id", "ID", col_type="number", width=80)
        grid_builder.add_column(
            "recipient_type", "Loại người nhận", col_type="text", width=150
        )
        grid_builder.add_column(
            "recipient_phone", "Số điện thoại", col_type="text", width=150
        )
        grid_builder.add_column("recipient_email", "Email", col_type="text", width=180)
        grid_builder.add_column("channel", "Kênh gửi", col_type="text", width=120)
        grid_builder.add_column("status", "Trạng thái", col_type="status", width=130)
        grid_builder.add_column(
            "created_at", "Ngày gửi", col_type="datetime", width=180
        )

        context = {
            "grid_id": grid_builder.grid_id,
            "api_url": grid_builder.api_url,
            "columns_json": grid_builder.get_columns_json(),
            "options_json": grid_builder.get_options_json(),
        }
        return render(request, "pages/notifications/list.html", context)


class NotificationListApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = NotificationListQuerySerializer(data=request.GET)
        if not serializer.is_valid():
            return JsonResponse({"error": serializer.errors}, status=400)

        validated_data = serializer.validated_data
        ordering = validated_data.get("ordering")
        if isinstance(ordering, str):
            ordering = [ordering]

        dto = NotificationListQueryDTO(
            tenant_id=validated_data.get("tenant_id"),
            status=validated_data.get("status"),
            channel=validated_data.get("channel"),
            recipient_type=validated_data.get("recipient_type"),
            ref_type=validated_data.get("ref_type"),
            ref_id=validated_data.get("ref_id"),
            search=validated_data.get("search") or None,
            ordering=ordering,
            limit=validated_data.get("limit", 20),
            offset=validated_data.get("offset", 0),
        )

        filters = {
            "tenant_id": dto.tenant_id,
            "status": dto.status,
            "channel": dto.channel,
            "recipient_type": dto.recipient_type,
            "ref_type": dto.ref_type,
            "ref_id": dto.ref_id,
        }

        notifications, total = NotificationProvider.list_notifications().execute(
            filters={k: v for k, v in filters.items() if v is not None},
            search=dto.search,
            ordering=dto.ordering,
            limit=dto.limit,
            offset=dto.offset,
        )

        response_serializer = NotificationResponseSerializer(notifications, many=True)
        return JsonResponse({"results": response_serializer.data, "total": total})
