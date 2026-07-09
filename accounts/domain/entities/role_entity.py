from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class RoleEntity:
    """Domain representation of a Role."""

    id: int | None
    uuid: uuid.UUID
    tenant_id: int
    name: str
    slug: str
    description: str | None
    is_system: bool
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    domain_events: list[Any] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Role name cannot be empty.")
        if not self.slug or not self.slug.strip():
            raise ValueError("Role slug cannot be empty.")
        if self.tenant_id <= 0:
            raise ValueError("Invalid tenant_id. Must be a positive integer.")

    def deactivate(self) -> None:
        self.is_active = False

    def activate(self) -> None:
        self.is_active = True

    def update_info(
        self, name: str, slug: str, description: str | None, is_active: bool
    ) -> None:
        self.name = name.strip()
        self.slug = slug.strip().lower()
        self.description = description.strip() if description else None
        self.is_active = is_active

    def update_timestamp(self, now: datetime) -> None:
        self.updated_at = now
