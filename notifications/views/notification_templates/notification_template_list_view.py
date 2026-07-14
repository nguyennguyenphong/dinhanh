from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.utils.grid import DjangoGridBuilder
from notifications.application.dtos.notification_templates.notification_template_list_query_dto import (
    NotificationTemplateListQueryDTO,
)
from notifications.providers.notification_provider import NotificationProvider
from notifications.serializers.notification_templates.notification_template_list_query_serializer import (
    NotificationTemplateListQuerySerializer,
)
from notifications.serializers.notification_templates.notification_template_response_serializer import (
    NotificationTemplateResponseSerializer,
)


class NotificationTemplateListView(LoginRequiredMixin, View):

    def get(self, request):
        grid_builder = DjangoGridBuilder(
            grid_id="template-grid",
            api_url=reverse("notification_template_list_api"),
            page_size=20,
        )
        grid_builder.add_column("idx", "STT", col_type="number", width=70, sortable=False, filter=False)
        grid_builder.add_column("code", "Mã", col_type="text", width=150)
        grid_builder.add_column("name", "Tên mẫu", col_type="text", width=250)
        grid_builder.add_column("channel", "Kênh gửi", col_type="text", width=120)
        grid_builder.add_column("is_active", "Trạng thái", col_type="status", width=150)
        grid_builder.add_column("created_at", "Ngày tạo", col_type="datetime", width=180)

        context = {
            "grid_id": grid_builder.grid_id,
            "api_url": grid_builder.api_url,
            "columns_json": grid_builder.get_columns_json(),
            "options_json": grid_builder.get_options_json(),
        }
        return render(request, "pages/notification_templates/list.html", context)


class NotificationTemplateListApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = NotificationTemplateListQuerySerializer(data=request.GET)
        if not serializer.is_valid():
            return JsonResponse({"error": serializer.errors}, status=400)

        validated_data = serializer.validated_data
        ordering = validated_data.get("ordering")
        if isinstance(ordering, str):
            ordering = [ordering]

        dto = NotificationTemplateListQueryDTO(
            tenant_id=validated_data.get("tenant_id"),
            channel=validated_data.get("channel"),
            is_active=validated_data.get("is_active"),
            search=validated_data.get("search") or None,
            ordering=ordering,
            limit=validated_data.get("limit", 20),
            offset=validated_data.get("offset", 0),
        )

        templates, total = NotificationProvider.list_templates().execute(
            filters={
                "tenant_id": dto.tenant_id,
                "channel": dto.channel,
                "is_active": dto.is_active,
            },
            search=dto.search,
            ordering=dto.ordering,
            limit=dto.limit,
            offset=dto.offset,
        )

        response_serializer = NotificationTemplateResponseSerializer(templates, many=True)
        return JsonResponse({"results": response_serializer.data, "total": total})
