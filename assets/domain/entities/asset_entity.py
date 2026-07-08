from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any


@dataclass
class AssetEntity:
    """
    Domain representation of a corporate fixed asset.
    """

    id: int | None
    tenant_id: int
    category_id: int | None
    branch_id: int | None
    assigned_to_id: int | None
    code: str
    name: str
    serial_number: str | None
    purchase_date: date | None
    purchase_price: Decimal | None
    depreciation_rate: Decimal | None
    current_value: Decimal | None
    warranty_expiry: date | None
    status: str
    notes: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    domain_events: list[Any] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.code or not self.code.strip():
            raise ValueError("Asset code cannot be empty.")
        if not self.name or not self.name.strip():
            raise ValueError("Asset name cannot be empty.")
        if self.tenant_id <= 0:
            raise ValueError("Invalid tenant_id. Must be a positive integer.")
        if self.purchase_price is not None and self.purchase_price < 0:
            raise ValueError("Purchase price cannot be negative.")
        if self.current_value is not None and self.current_value < 0:
            raise ValueError("Current value cannot be negative.")
        if self.depreciation_rate is not None and not (
            0 <= self.depreciation_rate <= 100
        ):
            raise ValueError("Depreciation rate must be between 0 and 100.")
        if self.status not in [
            "IN_USE",
            "MAINTENANCE",
            "DISPOSED",
            "LOST",
            "TRANSFERRED",
        ]:
            raise ValueError(f"Invalid asset status: {self.status}")

    def update_status(self, new_status: str, notes: str | None = None) -> None:
        if new_status not in [
            "IN_USE",
            "MAINTENANCE",
            "DISPOSED",
            "LOST",
            "TRANSFERRED",
        ]:
            raise ValueError(f"Invalid status: {new_status}")
        self.status = new_status
        if notes:
            self.notes = notes
