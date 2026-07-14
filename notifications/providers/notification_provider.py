from __future__ import annotations

from notifications.application.usecases import (
    DeleteNotificationTemplateUseCase,
    GetNotificationTemplateUseCase,
    ListNotificationTemplateUseCase,
    ListNotificationUseCase,
    NotificationCreateUseCase,
    NotificationTemplateCreateUseCase,
    NotificationTemplateUpdateUseCase,
    UpdateNotificationStatusUseCase,
    GetNotificationUseCase,
)
from notifications.repositories import (
    NotificationRepositoryImpl,
    NotificationTemplateRepositoryImpl,
)


class NotificationProvider:

    @staticmethod
    def _notification_repo() -> NotificationRepositoryImpl:
        return NotificationRepositoryImpl()

    @staticmethod
    def _template_repo() -> NotificationTemplateRepositoryImpl:
        return NotificationTemplateRepositoryImpl()

    # Use cases
    @classmethod
    def create_template(cls) -> NotificationTemplateCreateUseCase:
        return NotificationTemplateCreateUseCase(cls._template_repo())

    @classmethod
    def update_template(cls) -> NotificationTemplateUpdateUseCase:
        return NotificationTemplateUpdateUseCase(cls._template_repo())

    @classmethod
    def get_template(cls) -> GetNotificationTemplateUseCase:
        return GetNotificationTemplateUseCase(cls._template_repo())

    @classmethod
    def list_templates(cls) -> ListNotificationTemplateUseCase:
        return ListNotificationTemplateUseCase(cls._template_repo())

    @classmethod
    def delete_template(cls) -> DeleteNotificationTemplateUseCase:
        return DeleteNotificationTemplateUseCase(cls._template_repo())

    @classmethod
    def create_notification(cls) -> NotificationCreateUseCase:
        return NotificationCreateUseCase(cls._notification_repo())

    @classmethod
    def get_notification(cls) -> GetNotificationUseCase:
        return GetNotificationUseCase(cls._notification_repo())

    @classmethod
    def list_notifications(cls) -> ListNotificationUseCase:
        return ListNotificationUseCase(cls._notification_repo())

    @classmethod
    def update_notification_status(cls) -> UpdateNotificationStatusUseCase:
        return UpdateNotificationStatusUseCase(cls._notification_repo())
