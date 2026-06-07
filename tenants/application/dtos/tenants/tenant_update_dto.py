from dataclasses import dataclass
from typing import Any
from decimal import Decimal
from datetime import datetime

@dataclass
class TenantUpdateDTO:
    tenant_id: int | None
    code: str | None = None
    name: str | None = None
    plan: str | None = None
    currency: str | None = None
    exchange_rate: Decimal | None = None
    default_language: str | None = None
    timezone: str | None = None
    primary_color: str | None = None
    is_active: bool | None = None
    max_users: int | None = None
    max_branches: int | None = None
    max_vehicles: int | None = None
    subscription_started_at: datetime | None = None
    subscription_expires_at: datetime | None = None
    settings: dict[str, Any] | None = None
    domain: str | None = None
    logo_url: str | None = None