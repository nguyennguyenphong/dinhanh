from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class PermissionEntity:
    """Domain representation of a Permission."""

    id: int | None
    uuid: uuid.UUID
    tenant_id: int
    name: str
    codename: str
    module: str
    action: str
    parent_id: int | None
    is_system: bool
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    domain_events: list[Any] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Permission name cannot be empty.")
        if not self.codename or not self.codename.strip():
            raise ValueError("Permission codename cannot be empty.")
        if not self.module or not self.module.strip():
            raise ValueError("Permission module cannot be empty.")
        if not self.action or not self.action.strip():
            raise ValueError("Permission action cannot be empty.")
        if self.tenant_id <= 0:
            raise ValueError("Invalid tenant_id. Must be a positive integer.")

    def deactivate(self) -> None:
        self.is_active = False

    def activate(self) -> None:
        self.is_active = True

    def update_info(
        self,
        name: str,
        codename: str,
        module: str,
        action: str,
        parent_id: int | None,
        is_active: bool,
    ) -> None:
        self.name = name.strip()
        self.codename = codename.strip().lower()
        self.module = module.strip()
        self.action = action.strip()
        self.parent_id = parent_id
        self.is_active = is_active

    def update_timestamp(self, now: datetime) -> None:
        self.updated_at = now
