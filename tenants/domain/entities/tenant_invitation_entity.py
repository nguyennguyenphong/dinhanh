"""
Domain entities for Tenant Invitation bounded context.
Pure Python dataclasses — no Django ORM dependency here.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TenantInvitationEntity:
    id: int | None
    tenant_id: int
    email: str
    token: str
    status: str
    invited_by_id: int
    expires_at: datetime
    accepted_at: datetime | None = None
    created_at: datetime | None = None

    def is_expired(self, now: datetime) -> bool:
        return now > self.expires_at

    def is_usable(self, now: datetime) -> bool:
        return self.status == "PENDING" and not self.is_expired(now)
