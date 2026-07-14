from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class NotificationTemplateResponseDTO:
    id: int
    tenant_id: int
    code: str
    name: str
    channel: str
    subject: str | None
    body: str
    variables: list[str]
    is_active: bool
    created_at: datetime | None
    updated_at: datetime | None
