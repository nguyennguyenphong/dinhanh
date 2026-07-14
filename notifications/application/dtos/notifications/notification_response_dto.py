from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class NotificationResponseDTO:
    id: int
    tenant_id: int
    template_id: int | None
    recipient_type: str
    recipient_id: int | None
    recipient_phone: str | None
    recipient_email: str | None
    channel: str
    subject: str | None
    body: str
    status: str
    retry_count: int
    error_msg: str | None
    ref_type: str | None
    ref_id: int | None
    sent_at: datetime | None
    created_at: datetime | None
    updated_at: datetime | None
