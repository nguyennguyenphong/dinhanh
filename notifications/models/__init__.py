# Import models from module in this package
# This is to avoid circular imports
# Example:
# from notifications.models.notifications import Notification

from .notification_templates import NotificationTemplate
from .notifications import Notification
