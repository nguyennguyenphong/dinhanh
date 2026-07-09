from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PermissionCreateDto:
    tenant_id: int
    name: str
    codename: str
    module: str
    action: str
    parent_id: int | None = None
    is_system: bool = False
    is_active: bool = True
