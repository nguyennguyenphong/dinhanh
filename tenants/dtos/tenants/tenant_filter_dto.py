from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class TenantFilterDTO:
    """DTO capturing search, filters, and sorting params for listings."""
    search: Optional[str] = None
    plan: Optional[str] = None
    is_active: Optional[bool] = None
    order_by: str = "-created_at"