from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any


@dataclass
class BranchCreateDto:
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


@dataclass
class BranchUpdateDto:
    id: int
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


@dataclass
class BranchDetailDto:
    id: int
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
    created_at: datetime | None
    updated_at: datetime | None
