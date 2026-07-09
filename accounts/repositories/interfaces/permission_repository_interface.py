from __future__ import annotations

import uuid
from typing import Protocol

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
