from __future__ import annotations

from datetime import datetime

from django.utils import timezone

from notifications.application.dtos.notifications.notification_response_dto import (
    NotificationResponseDTO,
)
from notifications.application.usecases.notifications.mappers import (
    notification_entity_to_response,
)
from notifications.exceptions.exceptions import NotificationNotFoundError
from notifications.repositories.interfaces.notification_repository_interface import (
    INotificationRepository,
)


class UpdateNotificationStatusUseCase:

    def __init__(self, notification_repo: INotificationRepository):
        self._notification_repo = notification_repo

    def mark_sent(
        self, notification_id: int, sent_at: datetime | None = None
    ) -> NotificationResponseDTO:
        entity = self._notification_repo.get_by_id(notification_id)
        if not entity:
            raise NotificationNotFoundError(notification_id)

        now = sent_at or timezone.now()
        entity.mark_as_transmitted(now)
        updated = self._notification_repo.update(entity)
        return notification_entity_to_response(updated)

    def mark_failed(
        self, notification_id: int, error_msg: str
    ) -> NotificationResponseDTO:
        entity = self._notification_repo.get_by_id(notification_id)
        if not entity:
            raise NotificationNotFoundError(notification_id)

        entity.mark_as_failed(error_msg)
        updated = self._notification_repo.update(entity)
        return notification_entity_to_response(updated)
