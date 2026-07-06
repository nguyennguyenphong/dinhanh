# Import models from module in this package
# This is to avoid circular imports
# Example:
# from notifications.models.notifications import Notification

from notifications.models.notifications import Notification
from notifications.models.notification_templates import NotificationTemplate

__all__ = [
    "Notification",
    "NotificationTemplate",
]
