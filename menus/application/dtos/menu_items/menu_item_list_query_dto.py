from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MenuItemListQueryDto:
    """Dto to represent query parameters for listing menu items."""

    tenant_id: int
    group_id: int | None = None
    parent_id: int | None = None
    search: str | None = None
    is_active: bool | None = None
    ordering: list[str] | None = None
    limit: int = 20
    offset: int = 0
