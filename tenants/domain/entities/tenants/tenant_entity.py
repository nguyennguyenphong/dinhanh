# tenants/domain/entities/tenants/tenant_entity.py
from dataclasses import dataclass
from uuid import UUID

@dataclass
class TenantEntity:
    id: int
    uuid: UUID
    code: str
    is_active: bool
