"""
Abstract repository interfaces for the Tenant bounded context.
Concrete implementations live in repositories/implement/.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from tenants.domain.entities.tenant_entity import TenantEntity


class ITenantRepository(ABC):
    """Contract for Tenant persistence operations."""

    @abstractmethod
    def get_by_id(self, tenant_id: int) -> TenantEntity | None:
        ...

    @abstractmethod
    def get_by_uuid(self, uuid: str) -> TenantEntity | None:
        ...

    @abstractmethod
    def get_by_code(self, code: str) -> TenantEntity | None:
        ...

    @abstractmethod
    def list(
        self,
        *,
        filters: dict[str, Any] | None = None,
        search: str | None = None,
        ordering: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[TenantEntity], int]:
        """Returns (items, total_count)."""
        ...

    @abstractmethod
    def create(self, entity: TenantEntity) -> TenantEntity:
        ...

    @abstractmethod
    def update(self, entity: TenantEntity) -> TenantEntity:
        ...

    @abstractmethod
    def delete(self, tenant_id: int) -> None:
        """Hard delete — use with care; prefer deactivate."""
        ...

    @abstractmethod
    def deactivate(self, tenant_id: int) -> TenantEntity:
        ...

    @abstractmethod
    def exists_by_code(self, code: str, exclude_id: int | None = None) -> bool:
        ...
