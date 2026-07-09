from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UserCreateDto:
    tenant_id: int
    username: str
    email: str
    password: str
    full_name: str
    phone: str | None = None
    avatar: str | None = None
    is_active: bool = True
