from django.urls import include, path

urlpatterns = [
    path("", include("notifications.urls.notification_templates.urls")),
    path("", include("notifications.urls.notifications.urls")),
]
