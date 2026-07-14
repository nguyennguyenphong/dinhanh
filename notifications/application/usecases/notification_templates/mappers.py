from __future__ import annotations

from notifications.application.dtos.notification_templates.template_response_dto import (
    NotificationTemplateResponseDTO,
)
from notifications.domain.entities.notification_template_entity import (
    NotificationTemplateEntity,
)


def template_entity_to_response(
    entity: NotificationTemplateEntity,
) -> NotificationTemplateResponseDTO:
    return NotificationTemplateResponseDTO(
        id=entity.id,  # type: ignore
        tenant_id=entity.tenant_id,
        code=entity.code,
        name=entity.name,
        channel=entity.channel,
        subject=entity.subject,
        body=entity.body,
        variables=entity.variables,
        is_active=entity.is_active,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )
