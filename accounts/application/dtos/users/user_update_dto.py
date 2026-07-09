from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UserUpdateDto:
    full_name: str
    phone: str | None = None
    avatar: str | None = None
    is_active: bool = True
