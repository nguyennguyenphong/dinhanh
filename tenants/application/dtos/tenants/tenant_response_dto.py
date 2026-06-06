"""
Data Transfer Objects for Tenant CRUD operations.
Used by use-cases and serializers — no ORM/domain logic here.
"""
from __future__ import annotations
 
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any



@dataclass
class TenantResponseDTO:
    id: int
    uuid: str
    code: str
    name: str
    plan: str
    is_active: bool
    currency: str
    exchange_rate: Decimal
    default_language: str
    timezone: str
    primary_color: str
    max_users: int
    max_branches: int
    max_vehicles: int
    subscription_started_at: datetime | None
    subscription_expires_at: datetime | None
    settings: dict[str, Any]
    domain: str | None
    logo_url: str | None
    created_at: datetime | None
    updated_at: datetime | None