from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class StorageUnitCreateDto:
    tenant_id: int
    branch_id: int | None
    code: str
    name: str
    description: str | None


@dataclass(frozen=True)
class StorageUnitUpdateDto:
    id: int
    branch_id: int | None
    code: str
    name: str
    description: str | None


@dataclass(frozen=True)
class StorageUnitResponseDto:
    id: int
    tenant_id: int
    branch_id: int | None
    code: str
    name: str
    description: str | None
    created_at: datetime | None
    updated_at: datetime | None
