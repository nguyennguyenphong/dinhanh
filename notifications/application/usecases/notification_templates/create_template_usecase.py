from __future__ import annotations

from notifications.application.dtos.notification_templates.template_create_dto import (
    NotificationTemplateCreateDTO,
)
from notifications.application.dtos.notification_templates.template_response_dto import (
    NotificationTemplateResponseDTO,
)
from notifications.application.usecases.notification_templates.mappers import (
    template_entity_to_response,
)
from notifications.domain.entities.notification_template_entity import (
    NotificationTemplateEntity,
)
from notifications.exceptions.exceptions import NotificationTemplateAlreadyExistsError
from notifications.repositories.interfaces.notification_template_repository_interface import (
    INotificationTemplateRepository,
)


class CreateNotificationTemplateUseCase:

    def __init__(self, template_repo: INotificationTemplateRepository):
        self._template_repo = template_repo

    def execute(
        self, dto: NotificationTemplateCreateDTO
    ) -> NotificationTemplateResponseDTO:
        tenant_id = dto.tenant_id
        code = dto.code.upper().strip()
        channel = dto.channel

        if self._template_repo.exists_by_code_channel(tenant_id, code, channel):
            raise NotificationTemplateAlreadyExistsError(tenant_id, code, channel)

        entity = NotificationTemplateEntity(
            id=None,
            tenant_id=tenant_id,
            code=code,
            name=dto.name.strip(),
            channel=channel,
            subject=dto.subject,
            body=dto.body,
            variables=dto.variables,
            is_active=dto.is_active,
        )

        entity.validate()
        saved = self._template_repo.create(entity)
        return template_entity_to_response(saved)
