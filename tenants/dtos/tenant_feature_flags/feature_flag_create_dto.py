from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass(frozen=True)
class FeatureFlagCreateDTO:
    tenant_id: int
    code: str
    name: str
    description: Optional[str] = None
    is_enabled: bool = False
    rollout_percentage: int = 100
    config: Optional[Dict[str, Any]] = None