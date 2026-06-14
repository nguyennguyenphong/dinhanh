"""
Dependency injection provider for the Tenant bounded context.

Usage:
    from tenants.providers import TenantAuditLogProvider

    use_case = TenantProvider.create_tenant_use_case()
    result = use_case.execute(dto, actor_id=request.user.pk, ...)
"""

from __future__ import annotations

from tenants.application.usecases import ListAuditLogsUseCase
from tenants.repositories.implement import TenantAuditLogRepositoryImpl


class TenantAuditLogProvider:
    """
    Static factory — instantiates concrete repos and injects them into use-cases.
    Swap any repository implementation here without touching business logic.
    """

    # ------------------------------------------------------------------ #
    # Shared repository instances (stateless, safe to share per request)  #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _audit_repo() -> TenantAuditLogRepositoryImpl:
        return TenantAuditLogRepositoryImpl()

    # ------------------------------------------------------------------ #
    # Use-case factories                                                   #
    # ------------------------------------------------------------------ #

    @classmethod
    def list_audit_logs(cls) -> ListAuditLogsUseCase:
        return ListAuditLogsUseCase(cls._audit_repo())
