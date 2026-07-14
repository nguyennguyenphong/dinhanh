from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views import View
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from notifications.exceptions.exceptions import NotificationNotFoundError
from notifications.models.notifications import Notification
from notifications.providers.notification_provider import NotificationProvider
from notifications.serializers.notifications.notification_response_serializer import (
    NotificationResponseSerializer,
)


class NotificationDetailView(LoginRequiredMixin, View):

    def get(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk)
        return render(request, "pages/notifications/detail.html", {"object": notification})


class NotificationDetailApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            dto = NotificationProvider.get_notification().execute(pk)
            response_serializer = NotificationResponseSerializer(dto)
            return JsonResponse(response_serializer.data)
        except NotificationNotFoundError as e:
            return JsonResponse({"error": str(e)}, status=404)
