"""
Data Transfer Objects for Role listing queries.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RoleListQueryDto:
    tenant_id: int
    search: str | None = None
    is_active: bool | None = None
    ordering: list[str] | None = None
    limit: int = 20
    offset: int = 0
