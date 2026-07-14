from django.urls import path

from notifications.views import (
    NotificationTemplateCreateApiView,
    NotificationTemplateCreateView,
    NotificationTemplateDeleteApiView,
    NotificationTemplateDetailApiView,
    NotificationTemplateDetailView,
    NotificationTemplateListApiView,
    NotificationTemplateListView,
    NotificationTemplateUpdateApiView,
    NotificationTemplateUpdateView,
)

urlpatterns = [
    # UI Views
    path(
        "list/ui/",
        NotificationTemplateListView.as_view(),
        name="notification_template_list",
    ),
    path(
        "create/",
        NotificationTemplateCreateView.as_view(),
        name="notification_template_create",
    ),
    path(
        "detail/<int:pk>/",
        NotificationTemplateDetailView.as_view(),
        name="notification_template_detail",
    ),
    path(
        "update/<int:pk>/",
        NotificationTemplateUpdateView.as_view(),
        name="notification_template_update",
    ),
    # API Views
    path(
        "api/v1/list/",
        NotificationTemplateListApiView.as_view(),
        name="notification_template_list_api",
    ),
    path(
        "api/v1/create/",
        NotificationTemplateCreateApiView.as_view(),
        name="notification_template_create_api",
    ),
    path(
        "api/v1/detail/<int:pk>/",
        NotificationTemplateDetailApiView.as_view(),
        name="notification_template_detail_api",
    ),
    path(
        "api/v1/update/<int:pk>/",
        NotificationTemplateUpdateApiView.as_view(),
        name="notification_template_update_api",
    ),
    path(
        "api/v1/delete/<int:pk>/",
        NotificationTemplateDeleteApiView.as_view(),
        name="notification_template_delete",
    ),
]
