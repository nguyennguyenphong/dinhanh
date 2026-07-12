from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class UserResponseDto:
    id: int
    uuid: uuid.UUID
    tenant_id: int
    username: str
    email: str
    full_name: str
    phone: str | None
    avatar: str | None
    is_active: bool
    created_at: datetime | None
    updated_at: datetime | None
    branch_id: int | None = None
    must_change_password: bool = False
    password_expires_at: datetime | None = None
    locked_until: datetime | None = None

    @classmethod
    def from_entity(cls, entity: Any) -> UserResponseDto:
        return cls(
            id=entity.id,
            uuid=entity.uuid,
            tenant_id=entity.tenant_id,
            username=entity.username,
            email=entity.email,
            full_name=entity.full_name,
            phone=entity.phone,
            avatar=entity.avatar,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            branch_id=entity.branch_id,
            must_change_password=entity.must_change_password,
            password_expires_at=entity.password_expires_at,
            locked_until=entity.locked_until,
        )
