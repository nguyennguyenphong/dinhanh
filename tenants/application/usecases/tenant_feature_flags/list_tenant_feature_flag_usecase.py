"""
Use-cases for TenantFeatureFlag and TenantInvitation operations.
"""
from __future__ import annotations


from tenants.domain.entities.tenant_feature_flag_entity import TenantFeatureFlagEntity
from tenants.repositories.interfaces.tenant_feature_flag_interface import ITenantFeatureFlagRepository


class ListFeatureFlagsUseCase:
    def __init__(self, ff_repo: ITenantFeatureFlagRepository):
        self._ff_repo = ff_repo

    def execute(self, tenant_id: int) -> list[TenantFeatureFlagEntity]:
        return self._ff_repo.list_by_tenant(tenant_id)
