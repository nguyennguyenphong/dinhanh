from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Any

from menus.domain.entities import MenuGroupEntity


class IMenuGroupRepository(ABC):
    """
    Abstract repository interface for MenuGroup persistence operations.
    Handles both lifecycle tracking, standard queries, and deletion strategies.
    """

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    @abstractmethod
    def get_by_id(self, menu_group_id: int) -> MenuGroupEntity | None:
        """
        Fetches a MenuGroup by its database integer ID.
        Returns None if not found or soft-deleted.
        """
        ...

    @abstractmethod
    def get_by_uuid(self, group_uuid: uuid.UUID) -> MenuGroupEntity | None:
        """
        Fetches a MenuGroup by its globally unique UUID.
        """
        ...

    @abstractmethod
    def get_by_code(self, tenant_id: int, code: str) -> MenuGroupEntity | None:
        """
        Fetches a MenuGroup by its unique code within a specific tenant context.
        """
        ...

    @abstractmethod
    def list(
        self,
        *,
        tenant: int,
        filters: dict[str, Any] | None = None,
        search: str | None = None,
        ordering: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> tuple[list[MenuGroupEntity], int]:
        """
        Returns a paginated list of MenuGroupEntities and the total count.
        Allows toggling `include_deleted` to see soft-deleted items if needed (e.g., Trash bin UI).
        """
        ...

    @abstractmethod
    def exists_by_code(self, tenant: int, code: str, exclude_id: int | None = None) -> bool:
        """
        Validates uniqueness of a code within a tenant scope, excluding a specific ID during updates.
        """
        ...

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    @abstractmethod
    def create(self, entity: MenuGroupEntity) -> MenuGroupEntity:
        """
        Persists a new MenuGroupEntity into the database.
        """
        ...

    @abstractmethod
    def update(self, entity: MenuGroupEntity) -> MenuGroupEntity:
        """
        Updates an existing MenuGroupEntity in the database.
        """
        ...

    @abstractmethod
    def soft_delete(self, entity: MenuGroupEntity) -> None:
        """
        Flags the entity as deleted in the persistence layer without removing rows.
        Integrates with Django's SafeDeleteModel system.
        """
        ...

    @abstractmethod
    def hard_delete(self, entity: MenuGroupEntity) -> None:
        """
        CRITICAL: Permanently removes the record from the database.
        Use with extreme caution.
        """
        ...