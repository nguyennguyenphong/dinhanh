from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PermissionUpdateDto:
    name: str
    codename: str
    module: str
    action: str
    parent_id: int | None = None
    is_active: bool = True
