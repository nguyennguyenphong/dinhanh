from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any


@dataclass
class BranchEntity:
    """
    Domain representation of a corporate organization branch.
    """

    id: int | None
    tenant_id: int
    code: str
    name: str
    address: str | None
    phone: str | None
    email: str | None
    manager_id: int | None
    latitude: Decimal | None
    longitude: Decimal | None
    timezone: str
    is_active: bool
    metadata: dict[str, Any]
    created_at: datetime | None = None
    updated_at: datetime | None = None

    domain_events: list[Any] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.code or not self.code.strip():
            raise ValueError("Branch code cannot be empty.")
        if not self.name or not self.name.strip():
            raise ValueError("Branch name cannot be empty.")
        if self.tenant_id <= 0:
            raise ValueError("Tenant ID must be a positive integer.")
