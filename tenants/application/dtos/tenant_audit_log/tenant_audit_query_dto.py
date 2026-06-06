from dataclasses import dataclass


@dataclass
class TenantAuditLogQueryDTO:
    tenant_id: int
    action: str | None = None
    module: str | None = None
    limit: int = 50
    offset: int = 0