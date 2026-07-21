from django.shortcuts import render
from django.views import View

from notifications.views.forms import NotificationBaseForm


class NotificationSendView(View):
    def get(self, request):
        form = NotificationBaseForm()
        return render(request, "pages/notifications/send.html", {"form": form})
