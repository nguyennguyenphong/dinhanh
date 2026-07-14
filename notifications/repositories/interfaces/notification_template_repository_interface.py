from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from notifications.domain.entities.notification_template_entity import (
    NotificationTemplateEntity,
)


class INotificationTemplateRepository(ABC):

    @abstractmethod
    def get_by_id(self, template_id: int) -> NotificationTemplateEntity | None:
        pass

    @abstractmethod
    def get_by_code(
        self, tenant_id: int, code: str, channel: str
    ) -> NotificationTemplateEntity | None:
        pass

    @abstractmethod
    def list(
        self,
        *,
        filters: dict[str, Any] | None = None,
        search: str | None = None,
        ordering: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[NotificationTemplateEntity], int]:
        """Returns (items, total_count)."""
        pass

    @abstractmethod
    def create(
        self, entity: NotificationTemplateEntity
    ) -> NotificationTemplateEntity:
        pass

    @abstractmethod
    def update(
        self, entity: NotificationTemplateEntity
    ) -> NotificationTemplateEntity:
        pass

    @abstractmethod
    def delete(self, template_id: int) -> None:
        pass

    @abstractmethod
    def exists_by_code_channel(
        self, tenant_id: int, code: str, channel: str, exclude_id: int | None = None
    ) -> bool:
        pass
