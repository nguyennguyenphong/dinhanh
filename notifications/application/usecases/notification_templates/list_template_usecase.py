from __future__ import annotations

from typing import Any

from notifications.application.dtos.notification_templates.template_response_dto import (
    NotificationTemplateResponseDTO,
)
from notifications.application.usecases.notification_templates.mappers import (
    template_entity_to_response,
)
from notifications.repositories.interfaces.notification_template_repository_interface import (
    INotificationTemplateRepository,
)


class ListNotificationTemplatesUseCase:

    def __init__(self, template_repo: INotificationTemplateRepository):
        self._template_repo = template_repo

    def execute(
        self,
        *,
        filters: dict[str, Any] | None = None,
        search: str | None = None,
        ordering: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[NotificationTemplateResponseDTO], int]:
        entities, total = self._template_repo.list(
            filters=filters,
            search=search,
            ordering=ordering,
            limit=limit,
            offset=offset,
        )
        responses = [template_entity_to_response(entity) for entity in entities]
        return responses, total
