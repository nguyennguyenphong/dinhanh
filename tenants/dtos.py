"""
Domain Transfer Objects (DTOs) for tenants.

DTOs are used internally for inter-layer communication.
They are NOT the same as Serializers (which handle API I/O).

Example:
- DTO: TenantCreateDTO (used by UseCase)
- Serializer: TenantSerializer (used by API view)
"""

import uuid
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional


@dataclass
class TenantCreateDTO:
    """Input DTO for creating a tenant"""

    code: str
    name: str
    plan: str = "STANDARD"
    currency: str = "VND"
    exchange_rate: Decimal = Decimal("1.0000")
    default_language: str = "vi"
    timezone: str = "Asia/Ho_Chi_Minh"
    primary_color: str = "#3B82F6"
    settings: dict[str, Any] | None = None
    domain: Optional[str] = None
    logo_url: Optional[str] = None


@dataclass
class TenantResponseDTO:
    """Output DTO returned from services"""

    id: int
    uuid: uuid.UUID
    code: str
    name: str
    plan: str
    currency: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    # ... other fields


@dataclass
class TenantUpdateDTO:
    """Input DTO for updating a tenant"""

    tenant_id: int
    code: Optional[str] = None
    name: Optional[str] = None
    plan: Optional[str] = None
    is_active: Optional[bool] = None
    # ... other fields


@dataclass
class TenantListQueryDTO:
    """Input DTO for listing tenants with filters"""

    search: Optional[str] = None
    plan: Optional[str] = None
    is_active: Optional[bool] = None
    limit: int = 20
    offset: int = 0
