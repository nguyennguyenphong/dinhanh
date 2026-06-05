from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass(frozen=True)
class FeatureFlagUpdateDTO:
    name: Optional[str] = None
    description: Optional[str] = None
    is_enabled: Optional[bool] = None
    rollout_percentage: Optional[int] = None
    config: Optional[Dict[str, Any]] = None