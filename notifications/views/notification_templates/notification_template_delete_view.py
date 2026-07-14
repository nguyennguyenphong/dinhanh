from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from notifications.exceptions.exceptions import NotificationTemplateNotFoundError
from notifications.providers.notification_provider import NotificationProvider


class NotificationTemplateDeleteApiView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            NotificationProvider.delete_template().execute(pk)
            return JsonResponse({"message": "Template deleted successfully."}, status=200)
        except NotificationTemplateNotFoundError as e:
            return JsonResponse({"error": str(e)}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
