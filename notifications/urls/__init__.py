from django.urls import include, path

urlpatterns = [
    path("templates/", include("notifications.urls.notification_templates.urls")),
    path("logs/", include("notifications.urls.notifications.urls")),
]
