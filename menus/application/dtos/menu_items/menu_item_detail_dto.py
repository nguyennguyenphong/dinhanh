from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class MenuItemDetailDto:
    """Detailed MenuItem data used for the details page or updating form."""

    id: int
    uuid: uuid.UUID
    tenant_id: int
    code: str
    label: str
    group_id: int | None
    parent_id: int | None
    url_name: str | None
    url_path: str | None
    icon: str | None
    badge: str | None
    permission_code: str | None
    sort_order: int
    open_in_new_tab: bool
    is_active: bool
    is_hidden: bool
    created_at: datetime | None
    updated_at: datetime | None

    @classmethod
    def from_entity(cls, entity: Any) -> MenuItemDetailDto:
        """Factory method to map directly from MenuItemEntity to Detail DTO."""
        return cls(
            id=entity.id,
            uuid=entity.uuid,
            tenant_id=entity.tenant_id,
            code=entity.code,
            label=entity.label,
            group_id=entity.group_id,
            parent_id=entity.parent_id,
            url_name=entity.url_name,
            url_path=entity.url_path,
            icon=entity.icon,
            badge=entity.badge,
            permission_code=entity.permission_code,
            sort_order=entity.sort_order,
            open_in_new_tab=entity.open_in_new_tab,
            is_active=entity.is_active,
            is_hidden=entity.is_hidden,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
