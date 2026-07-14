from __future__ import annotations

from notifications.application.dtos.notification_templates.notification_template_response_dto import (
    NotificationTemplateResponseDTO,
)
from notifications.application.dtos.notification_templates.notification_template_update_dto import (
    NotificationTemplateUpdateDTO,
)
from notifications.application.usecases.notification_templates.mappers import (
    template_entity_to_response,
)
from notifications.domain.entities.notification_template_entity import (
    NotificationTemplateEntity,
)
from notifications.exceptions.exceptions import (
    NotificationTemplateAlreadyExistsError,
    NotificationTemplateNotFoundError,
)
from notifications.repositories.interfaces.notification_template_repository_interface import (
    INotificationTemplateRepository,
)


class NotificationTemplateUpdateUseCase:

    def __init__(self, template_repo: INotificationTemplateRepository):
        self._template_repo = template_repo

    def execute(
        self, dto: NotificationTemplateUpdateDTO
    ) -> NotificationTemplateResponseDTO:
        existing = self._template_repo.get_by_id(dto.id)
        if not existing:
            raise NotificationTemplateNotFoundError(dto.id)

        code = dto.code.upper().strip()
        if self._template_repo.exists_by_code_channel(
            dto.tenant_id, code, dto.channel, exclude_id=dto.id
        ):
            raise NotificationTemplateAlreadyExistsError(
                dto.tenant_id, code, dto.channel
            )

        entity = NotificationTemplateEntity(
            id=dto.id,
            tenant_id=dto.tenant_id,
            code=code,
            name=dto.name.strip(),
            channel=dto.channel,
            subject=dto.subject,
            body=dto.body,
            variables=dto.variables,
            is_active=dto.is_active,
        )

        entity.validate()
        updated = self._template_repo.update(entity)
        return template_entity_to_response(updated)
