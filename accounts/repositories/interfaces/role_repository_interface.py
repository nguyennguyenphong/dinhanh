from __future__ import annotations

import uuid
from typing import Any, Protocol

from accounts.domain.entities.role_entity import RoleEntity


class RoleRepository(Protocol):
    """Contract for role persistence operations."""

    def save(self, entity: RoleEntity) -> RoleEntity:
        """Save RoleEntity to persistence layer."""
        ...

    def find_by_uuid(self, role_uuid: uuid.UUID) -> RoleEntity | None:
        """Retrieve RoleEntity by its unique UUID."""
        ...

    def exists_by_slug(
        self, tenant_id: int, slug: str, exclude_id: int | None = None
    ) -> bool:
        """Check if slug exists in tenant, excluding specific ID if provided."""
        ...

    def delete(self, role_uuid: uuid.UUID) -> bool:
        """Soft-deactivate/delete a role."""
        ...

    def hard_delete(self, role_uuid: uuid.UUID) -> bool:
        """Hard-delete a role from database."""
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
    ) -> tuple[list[RoleEntity], int]:
        """List, filter, and page roles in a tenant context."""
        ...
