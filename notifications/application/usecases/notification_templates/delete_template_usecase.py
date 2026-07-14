from __future__ import annotations

from notifications.exceptions.exceptions import NotificationTemplateNotFoundError
from notifications.repositories.interfaces.notification_template_repository_interface import (
    INotificationTemplateRepository,
)


class DeleteNotificationTemplateUseCase:

    def __init__(self, template_repo: INotificationTemplateRepository):
        self._template_repo = template_repo

    def execute(self, template_id: int) -> None:
        existing = self._template_repo.get_by_id(template_id)
        if not existing:
            raise NotificationTemplateNotFoundError(template_id)
        self._template_repo.delete(template_id)
