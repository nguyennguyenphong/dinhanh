from __future__ import annotations

from dataclasses import dataclass


@dataclass
class NotificationListQueryDTO:
    tenant_id: int | None = None
    status: str | None = None
    channel: str | None = None
    recipient_type: str | None = None
    ref_type: str | None = None
    ref_id: int | None = None
    search: str | None = None
    ordering: list[str] | None = None
    limit: int = 20
    offset: int = 0
