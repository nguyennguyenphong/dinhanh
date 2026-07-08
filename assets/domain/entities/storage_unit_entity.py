from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class StorageUnitEntity:
    """
    Domain representation of a StorageUnit.
    """

    id: int | None
    tenant_id: int
    branch_id: int | None
    code: str
    name: str
    description: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    domain_events: list[Any] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.code or not self.code.strip():
            raise ValueError("StorageUnit code cannot be empty.")
        if not self.name or not self.name.strip():
            raise ValueError("StorageUnit name cannot be empty.")
        if self.tenant_id <= 0:
            raise ValueError("Invalid tenant_id. Must be a positive integer.")

    def update_details(self, name: str, description: str | None, branch_id: int | None) -> None:
        if not name or not name.strip():
            raise ValueError("Name cannot be empty.")
        self.name = name.strip()
        self.description = description
        self.branch_id = branch_id
