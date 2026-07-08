from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AssetCategoryCreateDto:
    tenant_id: int
    name: str


@dataclass(frozen=True)
class AssetCategoryUpdateDto:
    id: int
    name: str


@dataclass(frozen=True)
class AssetCategoryResponseDto:
    id: int
    tenant_id: int
    name: str
    created_at: datetime | None
    updated_at: datetime | None
