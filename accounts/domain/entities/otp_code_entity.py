from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class OTPCodeEntity:
    """
    Domain representation of an OTPCode.
    """

    id: int | None
    email: str
    code: str
    purpose: str
    expires_at: datetime
    is_used: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def is_expired(self, now: datetime) -> bool:
        return now > self.expires_at

    def mark_used(self) -> None:
        self.is_used = True
