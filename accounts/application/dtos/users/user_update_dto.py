from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class UserUpdateDto:
    full_name: str
    phone: str | None = None
    avatar: str | None = None
    is_active: bool = True
    tenant_id: int | None = None
    username: str | None = None
    email: str | None = None
    branch_id: int | None = None
    must_change_password: bool = False
    password_expires_at: datetime | None = None
    locked_until: datetime | None = None
