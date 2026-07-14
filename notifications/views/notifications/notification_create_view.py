from django.http import JsonResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from notifications.application.dtos.notifications.notification_create_dto import (
    NotificationCreateDTO,
)
from notifications.exceptions.exceptions import (
    NotificationDomainError,
    NotificationTemplateNotFoundError,
)
from notifications.providers.notification_provider import NotificationProvider
from notifications.serializers.notifications.notification_create_serializer import (
    NotificationCreateSerializer,
)
from notifications.serializers.notifications.notification_response_serializer import (
    NotificationResponseSerializer,
)
from notifications.services.notification_service import NotificationService


class NotificationCreateApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = NotificationCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse({"error": serializer.errors}, status=400)

        validated_data = serializer.validated_data
        dto = NotificationCreateDTO(
            tenant_id=validated_data.get("tenant_id", 1),
            template_id=validated_data.get("template_id"),
            recipient_type=validated_data["recipient_type"],
            recipient_id=validated_data.get("recipient_id"),
            recipient_phone=validated_data.get("recipient_phone"),
            recipient_email=validated_data.get("recipient_email"),
            channel=validated_data["channel"],
            subject=validated_data.get("subject"),
            body=validated_data["body"],
            ref_type=validated_data.get("ref_type"),
            ref_id=validated_data.get("ref_id"),
        )

        try:
            response_dto = NotificationProvider.create_notification().execute(dto)
            response_serializer = NotificationResponseSerializer(response_dto)
            return JsonResponse(response_serializer.data, status=201)
        except NotificationDomainError as e:
            return JsonResponse({"error": str(e)}, status=400)


class NotificationTriggerTemplatedApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        required_fields = [
            "tenant_id",
            "template_code",
            "channel",
            "recipient_type",
            "context",
        ]
        for field in required_fields:
            if field not in data:
                return JsonResponse(
                    {"error": f"Field '{field}' is required."}, status=400
                )

        try:
            notification_id = NotificationService.render_and_send(
                tenant_id=int(data["tenant_id"]),
                template_code=data["template_code"],
                channel=data["channel"],
                recipient_type=data["recipient_type"],
                context=data["context"],
                recipient_id=data.get("recipient_id"),
                recipient_phone=data.get("recipient_phone"),
                recipient_email=data.get("recipient_email"),
                ref_type=data.get("ref_type"),
                ref_id=data.get("ref_id"),
            )
            dto = NotificationProvider.get_notification().execute(notification_id)
            response_serializer = NotificationResponseSerializer(dto)
            return JsonResponse(response_serializer.data, status=201)
        except NotificationTemplateNotFoundError as e:
            return JsonResponse({"error": str(e)}, status=404)
        except KeyError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class NotificationDispatchNowApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        success = NotificationService.dispatch_now(pk)
        try:
            dto = NotificationProvider.get_notification().execute(pk)
            response_serializer = NotificationResponseSerializer(dto)
            if success:
                return JsonResponse(response_serializer.data)
            else:
                return JsonResponse(
                    {
                        "error": "Dispatch failed. Check logs for details.",
                        "details": response_serializer.data,
                    },
                    status=500,
                )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=404)


Answer = None
