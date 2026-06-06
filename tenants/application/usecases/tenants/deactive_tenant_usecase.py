"""
Use-cases for Tenant CRUD operations.
Each use-case class has a single public method and
orchestrates domain logic + repositories + audit logging.
"""
from __future__ import annotations


from tenants.application.dtos.tenants.tenant_response_dto import TenantResponseDTO
from tenants.domain.entities import TENANT_PLANS
from tenants.exceptions.exception import TenantNotFoundError
from tenants.repositories.interfaces.tenant_repository_interface import ITenantRepository
from tenants.repositories.interfaces.tenant_audit_log_repository_interface import ITenantAuditLogRepository

from tenants.application.usecases.tenants.tenant_usecase import _entity_to_response


class DeactivateTenantUseCase:
    """Soft-delete: sets is_active=False instead of hard-deleting."""

    def __init__(
        self,
        tenant_repo: ITenantRepository,
        audit_repo: ITenantAuditLogRepository,
    ):
        self._tenant_repo = tenant_repo
        self._audit_repo = audit_repo

    def execute(
        self,
        tenant_id: int,
        *,
        actor_id: int | None = None,
        actor_username: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TenantResponseDTO:
        entity = self._tenant_repo.get_by_id(tenant_id)
        if not entity:
            raise TenantNotFoundError(tenant_id)

        saved = self._tenant_repo.deactivate(tenant_id)

        self._audit_repo.create_log(
            tenant_id=saved.id,  # type: ignore[arg-type]
            user_id=actor_id,
            username=actor_username,
            action="DELETE",
            module="tenants",
            object_type="Tenant",
            object_id=str(saved.id),
            object_repr=str(saved),
            old_values={"is_active": True},
            new_values={"is_active": False},
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return _entity_to_response(saved)
