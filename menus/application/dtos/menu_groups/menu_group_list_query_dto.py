"""
Data Transfer Objects for Menu Group CRUD operations.
Used by use-cases and serializers — no ORM/domain logic here.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MenuGroupListQueryDto:
    tenant_id: int
    search: str | None = None
    is_active: bool | None = None
    ordering: list[str] | None = None
    limit: int = 20
    offset: int = 0
