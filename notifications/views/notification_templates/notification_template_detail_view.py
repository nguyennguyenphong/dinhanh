from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views import View
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from notifications.exceptions.exceptions import NotificationTemplateNotFoundError
from notifications.models.notification_templates import NotificationTemplate
from notifications.providers.notification_provider import NotificationProvider
from notifications.serializers.notification_templates.notification_template_response_serializer import (
    NotificationTemplateResponseSerializer,
)


class NotificationTemplateDetailView(LoginRequiredMixin, View):

    def get(self, request, pk):
        template = get_object_or_404(NotificationTemplate, pk=pk)
        return render(
            request, "pages/notification_templates/detail.html", {"object": template}
        )


class NotificationTemplateDetailApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            dto = NotificationProvider.get_template().by_id(pk)
            response_serializer = NotificationTemplateResponseSerializer(dto)
            return JsonResponse(response_serializer.data)
        except NotificationTemplateNotFoundError as e:
            return JsonResponse({"error": str(e)}, status=404)
