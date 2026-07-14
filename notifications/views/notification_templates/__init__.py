from notifications.views.notification_templates.notification_template_create_view import (
    NotificationTemplateCreateApiView,
    NotificationTemplateCreateView,
)
from notifications.views.notification_templates.notification_template_delete_view import (
    NotificationTemplateDeleteApiView,
)
from notifications.views.notification_templates.notification_template_detail_view import (
    NotificationTemplateDetailApiView,
    NotificationTemplateDetailView,
)
from notifications.views.notification_templates.notification_template_list_view import (
    NotificationTemplateListApiView,
    NotificationTemplateListView,
)
from notifications.views.notification_templates.notification_template_update_view import (
    NotificationTemplateUpdateApiView,
    NotificationTemplateUpdateView,
)

__all__ = [
    "NotificationTemplateListView",
    "NotificationTemplateListApiView",
    "NotificationTemplateCreateView",
    "NotificationTemplateCreateApiView",
    "NotificationTemplateDetailView",
    "NotificationTemplateDetailApiView",
    "NotificationTemplateUpdateView",
    "NotificationTemplateUpdateApiView",
    "NotificationTemplateDeleteApiView",
]
