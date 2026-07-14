from __future__ import annotations

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


class GetNotificationUseCase:

    def __init__(self, notification_repo: INotificationRepository):
        self._notification_repo = notification_repo

    def execute(self, notification_id: int) -> NotificationResponseDTO:
        entity = self._notification_repo.get_by_id(notification_id)
        if not entity:
            raise NotificationNotFoundError(notification_id)
        return notification_entity_to_response(entity)
