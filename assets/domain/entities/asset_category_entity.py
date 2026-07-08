from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class AssetCategoryEntity:
    """
    Domain representation of an AssetCategory.
    """

    id: int | None
    tenant_id: int
    name: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    domain_events: list[Any] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("AssetCategory name cannot be empty.")
        if self.tenant_id <= 0:
            raise ValueError("Invalid tenant_id. Must be a positive integer.")

    def update_name(self, name: str) -> None:
        if not name or not name.strip():
            raise ValueError("Name cannot be empty.")
        self.name = name.strip()
