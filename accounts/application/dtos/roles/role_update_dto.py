from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RoleUpdateDto:
    name: str
    slug: str
    description: str | None = None
    is_active: bool = True
