from __future__ import annotations

from notifications.application.dtos.notifications.notification_response_dto import (
    NotificationResponseDTO,
)
from notifications.domain.entities.notification_entity import NotificationEntity


def notification_entity_to_response(
    entity: NotificationEntity,
) -> NotificationResponseDTO:
    return NotificationResponseDTO(
        id=entity.id,  # type: ignore
        tenant_id=entity.tenant_id,
        template_id=entity.template_id,
        recipient_type=entity.recipient_type,
        recipient_id=entity.recipient_id,
        recipient_phone=entity.recipient_phone,
        recipient_email=entity.recipient_email,
        channel=entity.channel,
        subject=entity.subject,
        body=entity.body,
        status=entity.status,
        retry_count=entity.retry_count,
        error_msg=entity.error_msg,
        ref_type=entity.ref_type,
        ref_id=entity.ref_id,
        sent_at=entity.sent_at,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )
