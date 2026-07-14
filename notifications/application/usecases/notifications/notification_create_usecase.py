from __future__ import annotations

from django.db import transaction

from notifications.application.dtos.notifications.notification_create_dto import (
    NotificationCreateDTO,
)
from notifications.application.dtos.notifications.notification_response_dto import (
    NotificationResponseDTO,
)
from notifications.application.usecases.notifications.mappers import (
    notification_entity_to_response,
)
from notifications.domain.entities.notification_entity import NotificationEntity
from notifications.repositories.interfaces.notification_repository_interface import (
    INotificationRepository,
)


class NotificationCreateUseCase:

    def __init__(self, notification_repo: INotificationRepository):
        self._notification_repo = notification_repo

    def execute(self, dto: NotificationCreateDTO) -> NotificationResponseDTO:
        entity = NotificationEntity(
            id=None,
            tenant_id=dto.tenant_id,
            template_id=dto.template_id,
            recipient_type=dto.recipient_type,
            recipient_id=dto.recipient_id,
            recipient_phone=dto.recipient_phone,
            recipient_email=dto.recipient_email,
            channel=dto.channel,
            subject=dto.subject,
            body=dto.body,
            ref_type=dto.ref_type,
            ref_id=dto.ref_id,
        )

        entity.validate()

        with transaction.atomic():
            saved = self._notification_repo.create(entity)

            def trigger_async_dispatch(notification_id: int = saved.id):  # type: ignore
                from notifications.tasks.tasks import send_notification_async
                send_notification_async.delay(notification_id)

            transaction.on_commit(trigger_async_dispatch)

        return notification_entity_to_response(saved)
