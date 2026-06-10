"""
Use-cases for TenantFeatureFlag operations.
"""

from __future__ import annotations

from tenants.application.dtos.tenant_feature_flags.upsert_tenant_feature_flag_dto import (
    UpsertTenantFeatureFlagDTO,
)
from tenants.domain.entities.tenant_feature_flag_entity import TenantFeatureFlagEntity
from tenants.exceptions.exception import TenantNotFoundError
from tenants.repositories.interfaces.tenant_audit_log_repository_interface import (
    ITenantAuditLogRepository,
)
from tenants.repositories.interfaces.tenant_feature_flag_interface import (
    ITenantFeatureFlagRepository,
)
from tenants.repositories.interfaces.tenant_repository_interface import (
    ITenantRepository,
)


class UpsertTenantFeatureFlagUseCase:
    def __init__(
        self,
        tenant_repo: ITenantRepository,
        ff_repo: ITenantFeatureFlagRepository,
        audit_repo: ITenantAuditLogRepository,
    ):
        self._tenant_repo = tenant_repo
        self._ff_repo = ff_repo
        self._audit_repo = audit_repo

    def execute(
        self,
        dto: UpsertTenantFeatureFlagDTO,
        *,
        actor_id: int | None = None,
        actor_username: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TenantFeatureFlagEntity:
        tenant = self._tenant_repo.get_by_id(dto.tenant_id)
        if not tenant:
            raise TenantNotFoundError(dto.tenant_id)

        entity = TenantFeatureFlagEntity(
            id=None,
            tenant_id=dto.tenant_id,
            code=dto.code.upper().strip(),
            name=dto.name,
            description=dto.description,
            is_enabled=dto.is_enabled,
            rollout_percentage=dto.rollout_percentage,
            config=dto.config,
        )
        saved = self._ff_repo.upsert(entity)

        self._audit_repo.create_log(
            tenant_id=dto.tenant_id,
            user_id=actor_id,
            username=actor_username,
            action="UPDATE",
            module="feature_flags",
            object_type="TenantFeatureFlag",
            object_id=saved.code,
            object_repr=f"{saved.code} ({'ON' if saved.is_enabled else 'OFF'})",
            new_values={
                "code": saved.code,
                "is_enabled": saved.is_enabled,
                "rollout_percentage": saved.rollout_percentage,
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return saved
