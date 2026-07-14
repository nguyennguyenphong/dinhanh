from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from notifications.domain.entities.notification_entity import NotificationEntity


class INotificationRepository(ABC):

    @abstractmethod
    def get_by_id(self, notification_id: int) -> NotificationEntity | None:
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
    ) -> tuple[list[NotificationEntity], int]:
        """Returns (items, total_count)."""
        pass

    @abstractmethod
    def create(self, entity: NotificationEntity) -> NotificationEntity:
        pass

    @abstractmethod
    def update(self, entity: NotificationEntity) -> NotificationEntity:
        pass

    @abstractmethod
    def get_pending_notifications(self, limit: int = 50) -> list[NotificationEntity]:
        """Retrieve pending notifications for queue workers."""
        pass

    @abstractmethod
    def delete(self, notification_id: int) -> None:
        pass
