from typing import Any

from tenants.application.dtos.tenant_feature_flags import UpsertTenantFeatureFlagDTO
from tenants.domain.entities import TenantFeatureFlagEntity
from tenants.providers import TenantProvider


class TenantFeatureFlagService:
    @staticmethod
    def set_feature_flag(
        tenant_id: int,
        code: str,
        name: str,
        is_enabled: bool,
        rollout_percentage: int = 100,
        config: dict[str, Any] | None = None,
    ) -> TenantFeatureFlagEntity:
        dto = UpsertTenantFeatureFlagDTO(
            tenant_id=tenant_id,
            code=code,
            name=name,
            is_enabled=is_enabled,
            rollout_percentage=rollout_percentage,
            config=config or {},
        )
        return TenantProvider.upsert_feature_flag().execute(dto)

    @staticmethod
    def is_feature_enabled(tenant_id: int, code: str) -> bool:
        """
        Quick check for use in business logic across the codebase.
        Returns False if the flag doesn't exist.
        """
        flags = TenantProvider.list_feature_flags().execute(tenant_id)
        for flag in flags:
            if flag.code == code.upper():
                return flag.is_enabled
        return False