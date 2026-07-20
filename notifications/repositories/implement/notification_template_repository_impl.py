from __future__ import annotations

from typing import Any

from django.db.models import Q

from notifications.domain.entities.notification_template_entity import (
    NotificationTemplateEntity,
)
from notifications.repositories.interfaces.notification_template_repository_interface import (
    INotificationTemplateRepository,
)


def _model_to_entity(obj: Any) -> NotificationTemplateEntity:
    return NotificationTemplateEntity(
        id=obj.pk,
        tenant_id=obj.tenant_id,
        code=obj.code,
        name=obj.name,
        channel=obj.channel,
        subject=obj.subject,
        body=obj.body,
        variables=obj.variables or [],
        is_active=obj.is_active,
        created_at=obj.created_at,
        updated_at=obj.updated_at,
    )


class NotificationTemplateRepositoryImpl(INotificationTemplateRepository):

    @property
    def _qs(self):
        from notifications.models.notification_templates import NotificationTemplate

        return NotificationTemplate.objects

    def get_by_id(self, template_id: int) -> NotificationTemplateEntity | None:
        obj = self._qs.filter(pk=template_id).first()
        return _model_to_entity(obj) if obj else None

    def get_by_code(
        self, tenant_id: int, code: str, channel: str
    ) -> NotificationTemplateEntity | None:
        obj = self._qs.filter(
            tenant_id=tenant_id, code=code.upper(), channel=channel
        ).first()
        return _model_to_entity(obj) if obj else None

    def list(
        self,
        *,
        filters: dict[str, Any] | None = None,
        search: str | None = None,
        ordering: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[NotificationTemplateEntity], int]:
        qs = self._qs.all()

        if filters:
            if filters.get("tenant_id") is not None:
                qs = qs.filter(tenant_id=filters["tenant_id"])
            if filters.get("channel"):
                qs = qs.filter(channel=filters["channel"])
            if filters.get("is_active") is not None:
                qs = qs.filter(is_active=filters["is_active"])

        if search:
            qs = qs.filter(Q(code__icontains=search) | Q(name__icontains=search))

        total = qs.count()

        allowed_orderings = {
            "code",
            "-code",
            "channel",
            "-channel",
            "created_at",
            "-created_at",
        }
        if ordering:
            safe_ordering = [o for o in ordering if o in allowed_orderings]
            if safe_ordering:
                qs = qs.order_by(*safe_ordering)

        items = [_model_to_entity(obj) for obj in qs[offset : offset + limit]]
        return items, total

    def create(self, entity: NotificationTemplateEntity) -> NotificationTemplateEntity:
        from notifications.models.notification_templates import NotificationTemplate

        obj = NotificationTemplate.objects.create(
            tenant_id=entity.tenant_id,
            code=entity.code.upper().strip(),
            name=entity.name.strip(),
            channel=entity.channel,
            subject=entity.subject,
            body=entity.body,
            variables=entity.variables,
            is_active=entity.is_active,
        )
        return _model_to_entity(obj)

    def update(self, entity: NotificationTemplateEntity) -> NotificationTemplateEntity:
        from notifications.models.notification_templates import NotificationTemplate

        NotificationTemplate.objects.filter(pk=entity.id).update(
            tenant_id=entity.tenant_id,
            code=entity.code.upper().strip(),
            name=entity.name.strip(),
            channel=entity.channel,
            subject=entity.subject,
            body=entity.body,
            variables=entity.variables,
            is_active=entity.is_active,
        )
        return self.get_by_id(entity.id)  # type: ignore

    def delete(self, template_id: int) -> None:
        self._qs.filter(pk=template_id).delete()

    def exists_by_code_channel(
        self, tenant_id: int, code: str, channel: str, exclude_id: int | None = None
    ) -> bool:
        qs = self._qs.filter(tenant_id=tenant_id, code=code.upper(), channel=channel)
        if exclude_id:
            qs = qs.exclude(pk=exclude_id)
        return qs.exists()
