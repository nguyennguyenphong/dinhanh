"""
Dependency injection provider for the Tenant bounded context.

Usage:
    from tenants.providers import TenantFeatureFlagProvider

    use_case = TenantProvider.create_tenant_use_case()
    result = use_case.execute(dto, actor_id=request.user.pk, ...)
"""

from __future__ import annotations

from tenants.application.usecases import (
    DeleteFeatureFlagUseCase,
    ListFeatureFlagsUseCase,
    UpsertTenantFeatureFlagUseCase,
)
from tenants.repositories.implement import TenantFeatureFlagRepositoryImpl


class TenantFeatureFlagProvider:
    """
    Static factory — instantiates concrete repos and injects them into use-cases.
    Swap any repository implementation here without touching business logic.
    """

    @staticmethod
    def _ff_repo() -> TenantFeatureFlagRepositoryImpl:
        return TenantFeatureFlagRepositoryImpl()

    
    @classmethod
    def upsert_feature_flag(cls) -> UpsertTenantFeatureFlagUseCase:
        return UpsertTenantFeatureFlagUseCase(
            cls._tenant_repo(), cls._ff_repo(), cls._audit_repo()
        )

    @classmethod
    def delete_feature_flag(cls) -> DeleteFeatureFlagUseCase:
        return DeleteFeatureFlagUseCase(cls._ff_repo(), cls._audit_repo())

    @classmethod
    def list_feature_flags(cls) -> ListFeatureFlagsUseCase:
        return ListFeatureFlagsUseCase(cls._ff_repo())
