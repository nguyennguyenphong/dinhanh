from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from decimal import Decimal

@dataclass(frozen=True)
class TenantCreateDTO:
    """
    Data Transfer Object for creating a new Tenant.
    Encapsulates input parameters safely across system boundaries.
    """

    code: str
    name: str
    plan: str
    domain: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: str = "#3B82F6"
    currency: str = "VND"
    exchange_rate: Decimal = Decimal("1.0000")
    default_language: str = "vi"
    timezone: str = "Asia/Ho_Chi_Minh"
    max_users: Optional[int] = None
    max_branches: Optional[int] = None
    max_vehicles: Optional[int] = None
    settings: Dict[str, Any] = field(default_factory=dict)
    subscription_days: int = 30