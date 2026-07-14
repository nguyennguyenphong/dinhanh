from __future__ import annotations

from typing import Any

from django.db.models import Q

from notifications.domain.entities.notification_entity import NotificationEntity
from notifications.repositories.interfaces.notification_repository_interface import (
    INotificationRepository,
)


def _model_to_entity(obj: Any) -> NotificationEntity:
    return NotificationEntity(
        id=obj.id,
        tenant_id=obj.tenant_id,
        template_id=obj.template_id,
        recipient_type=obj.recipient_type,
        recipient_id=obj.recipient_id,
        recipient_phone=obj.recipient_phone,
        recipient_email=obj.recipient_email,
        channel=obj.channel,
        subject=obj.subject,
        body=obj.body,
        status=obj.status,
        retry_count=obj.retry_count,
        error_msg=obj.error_msg,
        ref_type=obj.ref_type,
        ref_id=obj.ref_id,
        sent_at=obj.sent_at,
        created_at=obj.created_at,
        updated_at=obj.updated_at,
    )


class NotificationRepositoryImpl(INotificationRepository):

    @property
    def _qs(self):
        from notifications.models.notifications import Notification

        return Notification.objects

    def get_by_id(self, notification_id: int) -> NotificationEntity | None:
        obj = self._qs.filter(pk=notification_id).first()
        return _model_to_entity(obj) if obj else None

    def list(
        self,
        *,
        filters: dict[str, Any] | None = None,
        search: str | None = None,
        ordering: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[NotificationEntity], int]:
        qs = self._qs.all()

        if filters:
            if filters.get("tenant_id") is not None:
                qs = qs.filter(tenant_id=filters["tenant_id"])
            if filters.get("status"):
                qs = qs.filter(status=filters["status"])
            if filters.get("channel"):
                qs = qs.filter(channel=filters["channel"])
            if filters.get("recipient_type"):
                qs = qs.filter(recipient_type=filters["recipient_type"])
            if filters.get("ref_type") and filters.get("ref_id"):
                qs = qs.filter(ref_type=filters["ref_type"], ref_id=filters["ref_id"])

        if search:
            qs = qs.filter(
                Q(recipient_email__icontains=search)
                | Q(recipient_phone__icontains=search)
                | Q(subject__icontains=search)
                | Q(body__icontains=search)
            )

        total = qs.count()

        allowed_orderings = {"created_at", "-created_at", "status", "-status"}
        if ordering:
            safe_ordering = [o for o in ordering if o in allowed_orderings]
            if safe_ordering:
                qs = qs.order_by(*safe_ordering)

        items = [_model_to_entity(obj) for obj in qs[offset : offset + limit]]
        return items, total

    def create(self, entity: NotificationEntity) -> NotificationEntity:
        from notifications.models.notifications import Notification

        obj = Notification.objects.create(
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
        )
        return _model_to_entity(obj)

    def update(self, entity: NotificationEntity) -> NotificationEntity:
        from notifications.models.notifications import Notification

        Notification.objects.filter(pk=entity.id).update(
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
        )
        return self.get_by_id(entity.id)  # type: ignore

    def get_pending_notifications(self, limit: int = 50) -> list[NotificationEntity]:
        # Optimize fetch order by composite status index
        objs = self._qs.filter(status="PENDING").order_by("created_at")[:limit]
        return [_model_to_entity(obj) for obj in objs]

    def delete(self, notification_id: int) -> None:
        self._qs.filter(pk=notification_id).delete()
