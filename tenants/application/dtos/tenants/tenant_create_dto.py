"""
Data Transfer Objects for Tenant CRUD operations.
Used by use-cases and serializers — no ORM/domain logic here.
"""
from __future__ import annotations
 
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any
 
 
@dataclass
class TenantCreateDTO:
    code: str
    name: str
    plan: str = "STANDARD"
    currency: str = "VND"
    exchange_rate: Decimal = Decimal("1.0000")
    default_language: str = "vi"
    timezone: str = "Asia/Ho_Chi_Minh"
    primary_color: str = "#3B82F6"
    max_users: int = 10
    max_branches: int = 1
    max_vehicles: int = 50
    subscription_started_at: datetime | None = None
    subscription_expires_at: datetime | None = None
    settings: dict[str, Any] = field(default_factory=dict)
    domain: str | None = None
    logo_url: str | None = None
    is_active: bool = True
 