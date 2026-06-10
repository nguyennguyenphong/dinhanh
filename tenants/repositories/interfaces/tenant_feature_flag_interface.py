"""
Abstract repository interfaces for the Tenant Feature Flag bounded context.
Concrete implementations live in repositories/implement/.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from tenants.domain.entities.tenant_feature_flag_entity import TenantFeatureFlagEntity


class ITenantFeatureFlagRepository(ABC):
    """Contract for feature flag persistence."""

    @abstractmethod
    def get_by_code(
        self, tenant_id: int, code: str
    ) -> TenantFeatureFlagEntity | None: ...

    @abstractmethod
    def list_by_tenant(self, tenant_id: int) -> list[TenantFeatureFlagEntity]: ...

    @abstractmethod
    def upsert(self, entity: TenantFeatureFlagEntity) -> TenantFeatureFlagEntity: ...

    @abstractmethod
    def delete(self, tenant_id: int, code: str) -> None: ...
