"""
Domain-level exceptions for the Notification bounded context.
"""


class NotificationDomainError(Exception):
    """Base class for all notification domain errors."""


class NotificationNotFoundError(NotificationDomainError):
    def __init__(self, notification_id: int):
        super().__init__(f"Notification log not found with ID: {notification_id}")
        self.notification_id = notification_id


class NotificationTemplateNotFoundError(NotificationDomainError):
    def __init__(self, identifier: str | int):
        super().__init__(f"Notification Template not found: {identifier}")
        self.identifier = identifier


class NotificationTemplateAlreadyExistsError(NotificationDomainError):
    def __init__(self, tenant_id: int, code: str, channel: str):
        super().__init__(
            f"Notification Template with code '{code}' and channel '{channel}' already exists for tenant {tenant_id}."
        )
        self.tenant_id = tenant_id
        self.code = code
        self.channel = channel
