"""
Dependency injection provider for the Tenant bounded context.

Usage:
    from tenants.providers import TenantProvider

    use_case = TenantProvider.create_tenant_use_case()
    result = use_case.execute(dto, actor_id=request.user.pk, ...)
"""

from __future__ import annotations

from tenants.application.usecases import (
    CreateTenantUseCase,
    DeactivateTenantUseCase,
    GetTenantUseCase,
    HardDeleteTenantUseCase,
    ListTenantsUseCase,
    UpdateTenantUseCase,
)
from tenants.repositories.implement import TenantRepositoryImpl


class TenantProvider:
    """
    Static factory — instantiates concrete repos and injects them into use-cases.
    Swap any repository implementation here without touching business logic.
    """

    # ------------------------------------------------------------------ #
    # Shared repository instances (stateless, safe to share per request)  #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _tenant_repo() -> TenantRepositoryImpl:
        return TenantRepositoryImpl()
    
    @staticmethod
    def _audit_repo():
        from tenants.providers.tenant_audit_log_provider import TenantAuditLogProvider
        return TenantAuditLogProvider._audit_repo()

    # ------------------------------------------------------------------ #
    # Use-case factories                                                   #
    # ------------------------------------------------------------------ #

    @classmethod
    def create_tenant(cls) -> CreateTenantUseCase:
        return CreateTenantUseCase(cls._tenant_repo(), cls._audit_repo())

    @classmethod
    def get_tenant(cls) -> GetTenantUseCase:
        return GetTenantUseCase(cls._tenant_repo())

    @classmethod
    def list_tenants(cls) -> ListTenantsUseCase:
        return ListTenantsUseCase(cls._tenant_repo())

    @classmethod
    def update_tenant(cls) -> UpdateTenantUseCase:
        return UpdateTenantUseCase(cls._tenant_repo(), cls._audit_repo())

    @classmethod
    def deactivate_tenant(cls) -> DeactivateTenantUseCase:
        return DeactivateTenantUseCase(cls._tenant_repo(), cls._audit_repo())

    @classmethod
    def hard_delete_tenant(cls) -> HardDeleteTenantUseCase:
        return HardDeleteTenantUseCase(cls._tenant_repo(), cls._audit_repo())

