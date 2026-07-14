from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class NotificationCreateDTO:
    tenant_id: int
    recipient_type: str
    channel: str
    body: str
    template_id: int | None = None
    recipient_id: int | None = None
    recipient_phone: str | None = None
    recipient_email: str | None = None
    subject: str | None = None
    ref_type: str | None = None
    ref_id: int | None = None
