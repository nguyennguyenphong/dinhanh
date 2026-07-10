"""
Data Transfer Objects for Permission listing queries.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PermissionListQueryDto:
    tenant_id: int
    search: str | None = None
    is_active: bool | None = None
    ordering: list[str] | None = None
    limit: int = 20
    offset: int = 0
