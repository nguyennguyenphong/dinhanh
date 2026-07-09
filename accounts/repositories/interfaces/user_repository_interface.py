from __future__ import annotations

import uuid
from typing import Protocol

from accounts.domain.entities.user_entity import UserEntity


class UserRepository(Protocol):
    """
    Contract for user persistence operations.
    """

    def save(self, entity: UserEntity) -> UserEntity:
        """Save UserEntity to persistence layer."""
        pass

    def find_by_uuid(self, user_uuid: uuid.UUID) -> UserEntity | None:
        """Retrieve UserEntity by its unique UUID."""
        pass

    def exists_by_username(
        self, tenant_id: int, username: str, exclude_id: int | None = None
    ) -> bool:
        """Check if username exists in tenant, excluding specific ID if provided."""
        pass

    def exists_by_email(
        self, tenant_id: int, email: str, exclude_id: int | None = None
    ) -> bool:
        """Check if email exists in tenant, excluding specific ID if provided."""
        pass

    def delete(self, user_uuid: uuid.UUID) -> bool:
        """Soft-deactivate a user."""
        pass

    def hard_delete(self, user_uuid: uuid.UUID) -> bool:
        """Hard-delete a user from database."""
        pass
