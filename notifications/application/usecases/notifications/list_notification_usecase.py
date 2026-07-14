from __future__ import annotations

from typing import Any

from notifications.application.dtos.notifications.notification_response_dto import (
    NotificationResponseDTO,
)
from notifications.application.usecases.notifications.mappers import (
    notification_entity_to_response,
)
from notifications.repositories.interfaces.notification_repository_interface import (
    INotificationRepository,
)


class ListNotificationUseCase:

    def __init__(self, notification_repo: INotificationRepository):
        self._notification_repo = notification_repo

    def execute(
        self,
        *,
        filters: dict[str, Any] | None = None,
        search: str | None = None,
        ordering: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[NotificationResponseDTO], int]:
        entities, total = self._notification_repo.list(
            filters=filters,
            search=search,
            ordering=ordering,
            limit=limit,
            offset=offset,
        )
        responses = [notification_entity_to_response(entity) for entity in entities]
        return responses, total
