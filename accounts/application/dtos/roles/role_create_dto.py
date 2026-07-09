from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RoleCreateDto:
    tenant_id: int
    name: str
    slug: str
    description: str | None = None
    is_system: bool = False
    is_active: bool = True
