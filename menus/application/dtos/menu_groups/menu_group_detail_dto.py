from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class MenuGroupDetailDto:
    """
    Detailed data is used for the Details page or to fill in the Update form.
    The list of submenus (MenuItems) can be expanded later if needed.
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
    # items: list[MenuItemDto] = field(default_factory=list)

    @classmethod
    def from_entity(cls, entity: Any) -> MenuGroupDetailDto:
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