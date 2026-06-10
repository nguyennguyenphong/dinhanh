"""
Django ORM concrete implementations for:
  - TenantFeatureFlag
"""

from __future__ import annotations

from typing import Any

from tenants.domain.entities.tenant_feature_flag_entity import TenantFeatureFlagEntity
from tenants.repositories.interfaces.tenant_feature_flag_interface import (
    ITenantFeatureFlagRepository,
)


def _ff_model_to_entity(obj: Any) -> TenantFeatureFlagEntity:
    return TenantFeatureFlagEntity(
        id=obj.pk,
        tenant_id=obj.tenant_id,
        code=obj.code,
        name=obj.name,
        description=obj.description,
        is_enabled=obj.is_enabled,
        rollout_percentage=obj.rollout_percentage,
        config=obj.config or {},
        created_at=obj.created_at,
        updated_at=obj.updated_at,
    )


class TenantFeatureFlagRepositoryImpl(ITenantFeatureFlagRepository):

    def get_by_code(self, tenant_id: int, code: str) -> TenantFeatureFlagEntity | None:
        from tenants.models.tenent_feature_flag import TenantFeatureFlag

        obj = TenantFeatureFlag.objects.filter(tenant_id=tenant_id, code=code).first()
        return _ff_model_to_entity(obj) if obj else None

    def list_by_tenant(self, tenant_id: int) -> list[TenantFeatureFlagEntity]:
        from tenants.models.tenent_feature_flag import TenantFeatureFlag

        return [
            _ff_model_to_entity(obj)
            for obj in TenantFeatureFlag.objects.filter(tenant_id=tenant_id)
        ]

    def upsert(self, entity: TenantFeatureFlagEntity) -> TenantFeatureFlagEntity:
        from tenants.models.tenent_feature_flag import TenantFeatureFlag

        obj, _ = TenantFeatureFlag.objects.update_or_create(
            tenant_id=entity.tenant_id,
            code=entity.code,
            defaults={
                "name": entity.name,
                "description": entity.description,
                "is_enabled": entity.is_enabled,
                "rollout_percentage": entity.rollout_percentage,
                "config": entity.config,
            },
        )
        return _ff_model_to_entity(obj)

    def delete(self, tenant_id: int, code: str) -> None:
        from tenants.models.tenent_feature_flag import TenantFeatureFlag

        TenantFeatureFlag.objects.filter(tenant_id=tenant_id, code=code).delete()
