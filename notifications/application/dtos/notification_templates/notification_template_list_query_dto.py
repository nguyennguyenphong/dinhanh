from __future__ import annotations

from dataclasses import dataclass


@dataclass
class NotificationTemplateListQueryDTO:
    tenant_id: int | None = None
    channel: str | None = None
    is_active: bool | None = None
    search: str | None = None
    ordering: list[str] | None = None
    limit: int = 20
    offset: int = 0
