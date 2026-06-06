"""
Data Transfer Objects for Tenant CRUD operations.
Used by use-cases and serializers — no ORM/domain logic here.
"""
from __future__ import annotations
 
from dataclasses import dataclass, field


@dataclass
class TenantListQueryDTO:
    search: str | None = None
    plan: str | None = None
    is_active: bool | None = None
    ordering: list[str] = field(default_factory=lambda: ["-created_at"])
    limit: int = 20
    offset: int = 0
 