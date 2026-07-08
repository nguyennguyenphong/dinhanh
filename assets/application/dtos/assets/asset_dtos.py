from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class AssetCreateDto:
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


@dataclass(frozen=True)
class AssetUpdateDto:
    id: int
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


@dataclass(frozen=True)
class AssetResponseDto:
    id: int
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
    created_at: datetime | None
    updated_at: datetime | None
