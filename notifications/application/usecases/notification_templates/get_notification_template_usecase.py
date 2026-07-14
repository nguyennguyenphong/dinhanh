from __future__ import annotations

from notifications.application.dtos.notification_templates.notification_template_response_dto import (
    NotificationTemplateResponseDTO,
)
from notifications.application.usecases.notification_templates.mappers import (
    template_entity_to_response,
)
from notifications.exceptions.exceptions import NotificationTemplateNotFoundError
from notifications.repositories.interfaces.notification_template_repository_interface import (
    INotificationTemplateRepository,
)


class GetNotificationTemplateUseCase:

    def __init__(self, template_repo: INotificationTemplateRepository):
        self._template_repo = template_repo

    def by_id(self, template_id: int) -> NotificationTemplateResponseDTO:
        entity = self._template_repo.get_by_id(template_id)
        if not entity:
            raise NotificationTemplateNotFoundError(template_id)
        return template_entity_to_response(entity)

    def by_code(
        self, tenant_id: int, code: str, channel: str
    ) -> NotificationTemplateResponseDTO:
        entity = self._template_repo.get_by_code(tenant_id, code, channel)
        if not entity:
            raise NotificationTemplateNotFoundError(f"{code} ({channel})")
        return template_entity_to_response(entity)
