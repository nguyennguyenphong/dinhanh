from dataclasses import dataclass, field
from typing import Any


@dataclass
class UpsertTenantFeatureFlagDTO:
    tenant_id: int
    code: str
    name: str
    is_enabled: bool
    rollout_percentage: int = 100
    config: dict[str, Any] = field(default_factory=dict)
    description: str | None = None
