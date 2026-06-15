from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class MenuGroupResponseDto:
    """
    A basic DTO represents a clean MenuGroup Object.
    It is often used as a baseline or returned after successful write operations.
    """
    id: int
    uuid: uuid.UUID
    tenant_id: int
    code: str
    label: str
    icon: str | None
    sort_order: int
    is_active: bool
    created_at: datetime | None
    updated_at: datetime | None

    @classmethod
    def from_entity(cls, entity: Any) -> MenuGroupResponseDto:
        """Factory methods map directly from Domain Entity to DTO."""
        return cls(
            id=entity.id,
            uuid=entity.uuid,
            tenant_id=entity.tenant_id,
            code=entity.code,
            label=entity.label,
            icon=entity.icon,
            sort_order=entity.sort_order,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )