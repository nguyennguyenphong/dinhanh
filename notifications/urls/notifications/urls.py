from django.urls import path

from notifications.views import (
    NotificationCreateApiView,
    NotificationDetailApiView,
    NotificationDetailView,
    NotificationListApiView,
    NotificationListView,
    NotificationTriggerTemplatedApiView,
    NotificationDispatchNowApiView,
)

urlpatterns = [
    # UI Views
    path("list/ui/", NotificationListView.as_view(), name="notification_log_list"),
    path("detail/<int:pk>/", NotificationDetailView.as_view(), name="notification_log_detail"),

    # API Views
    path("api/v1/list/", NotificationListApiView.as_view(), name="notification_log_list_api"),
    path("api/v1/create/", NotificationCreateApiView.as_view(), name="notification_log_create"),
    path("api/v1/detail/<int:pk>/", NotificationDetailApiView.as_view(), name="notification_log_detail_api"),
    path("api/v1/trigger-templated/", NotificationTriggerTemplatedApiView.as_view(), name="notification_trigger_templated"),
    path("api/v1/<int:pk>/dispatch/", NotificationDispatchNowApiView.as_view(), name="notification_dispatch_now"),
]
