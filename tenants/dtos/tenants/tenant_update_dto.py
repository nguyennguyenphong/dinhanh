from dataclasses import dataclass
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime

@dataclass(frozen=True)
class TenantUpdateDTO:
    """
    Data Transfer Object for updating an existing Tenant.
    Allows partial attributes modifications safely.
    """

    name: Optional[str] = None
    domain: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    plan: Optional[str] = None
    currency: Optional[str] = None
    exchange_rate: Optional[Decimal] = None
    default_language: Optional[str] = None
    timezone: Optional[str] = None
    is_active: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None
    max_users: Optional[int] = None
    max_branches: Optional[int] = None
    max_vehicles: Optional[int] = None
    subscription_expires_at: Optional[datetime] = None