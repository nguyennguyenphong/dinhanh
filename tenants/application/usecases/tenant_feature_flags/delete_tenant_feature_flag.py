"""
Use-cases for TenantFeatureFlag operations.
"""
from __future__ import annotations


from tenants.exceptions.exception import TenantFeatureFlagNotFoundError
from tenants.repositories.interfaces.tenant_audit_log_repository_interface import ITenantAuditLogRepository
from tenants.repositories.interfaces.tenant_feature_flag_interface import ITenantFeatureFlagRepository



class DeleteFeatureFlagUseCase:
    def __init__(
        self,
        ff_repo: ITenantFeatureFlagRepository,
        audit_repo: ITenantAuditLogRepository,
    ):
        self._ff_repo = ff_repo
        self._audit_repo = audit_repo

    def execute(
        self,
        tenant_id: int,
        code: str,
        *,
        actor_id: int | None = None,
        actor_username: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        flag = self._ff_repo.get_by_code(tenant_id, code.upper())
        if not flag:
            raise TenantFeatureFlagNotFoundError(code)

        self._ff_repo.delete(tenant_id, code.upper())

        self._audit_repo.create_log(
            tenant_id=tenant_id,
            user_id=actor_id,
            username=actor_username,
            action="DELETE",
            module="feature_flags",
            object_type="TenantFeatureFlag",
            object_id=code,
            ip_address=ip_address,
            user_agent=user_agent,
        )