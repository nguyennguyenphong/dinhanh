"""
Domain entities for Tenant Feature Flag bounded context.
Pure Python dataclasses — no Django ORM dependency here.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class TenantFeatureFlagEntity:
    id: int | None
    tenant_id: int
    code: str
    name: str
    is_enabled: bool
    rollout_percentage: int
    config: dict[str, Any]
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def is_rolled_out_for(self, user_bucket: int) -> bool:
        """
        user_bucket is typically hash(user_id) % 100.
        Returns True if this flag applies to that bucket.
        """
        if not self.is_enabled:
            return False
        return user_bucket < self.rollout_percentage
