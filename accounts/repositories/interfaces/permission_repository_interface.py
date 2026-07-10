from __future__ import annotations

import uuid
from typing import Protocol, Any

from accounts.domain.entities.permission_entity import PermissionEntity


class PermissionRepository(Protocol):
    """Contract for permission persistence operations."""

    def save(self, entity: PermissionEntity) -> PermissionEntity:
        """Save PermissionEntity to persistence layer."""
        ...

    def find_by_uuid(self, permission_uuid: uuid.UUID) -> PermissionEntity | None:
        """Retrieve PermissionEntity by its unique UUID."""
        ...

    def exists_by_codename(
        self, tenant_id: int, codename: str, exclude_id: int | None = None
    ) -> bool:
        """Check if codename exists in tenant, excluding specific ID if provided."""
        ...

    def delete(self, permission_uuid: uuid.UUID) -> bool:
        """Soft-deactivate/delete a permission."""
        ...

    def hard_delete(self, permission_uuid: uuid.UUID) -> bool:
        """Hard-delete a permission from database."""
        ...

    def list(
        self,
        *,
        tenant_id: int,
        filters: dict[str, Any] | None = None,
        search: str | None = None,
        ordering: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[PermissionEntity], int]:
        """List, filter, and page permissions in a tenant context."""
        ...
