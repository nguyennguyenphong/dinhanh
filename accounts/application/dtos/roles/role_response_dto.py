from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class RoleResponseDto:
    id: int
    uuid: uuid.UUID
    tenant_id: int
    name: str
    slug: str
    description: str | None
    is_system: bool
    is_active: bool
    created_at: datetime | None
    updated_at: datetime | None

    @classmethod
    def from_entity(cls, entity: Any) -> RoleResponseDto:
        return cls(
            id=entity.id,
            uuid=entity.uuid,
            tenant_id=entity.tenant_id,
            name=entity.name,
            slug=entity.slug,
            description=entity.description,
            is_system=entity.is_system,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
