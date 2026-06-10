"""
Use-cases for TenantAuditLog operations.
"""

from __future__ import annotations

from tenants.application.dtos.tenant_audit_log.tenant_audit_query_dto import (
    TenantAuditLogQueryDTO,
)
from tenants.repositories.interfaces.tenant_audit_log_repository_interface import (
    ITenantAuditLogRepository,
)


class ListAuditLogsUseCase:
    def __init__(self, audit_repo: ITenantAuditLogRepository):
        self._audit_repo = audit_repo

    def execute(self, query: TenantAuditLogQueryDTO) -> tuple[list[dict], int]:
        return self._audit_repo.list_by_tenant(
            query.tenant_id,
            action=query.action,
            module=query.module,
            limit=query.limit,
            offset=query.offset,
        )
