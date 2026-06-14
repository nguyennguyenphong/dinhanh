"""
Use-cases for Tenant CRUD operations.
Each use-case class has a single public method and
orchestrates domain logic + repositories + audit logging.
"""

from __future__ import annotations

from django.db import transaction

from tenants.application.usecases.tenants.tenant_usecase import _entity_to_audit_values
from tenants.exceptions.exception import TenantNotFoundError
from tenants.repositories.interfaces.tenant_audit_log_repository_interface import ITenantAuditLogRepository
from tenants.repositories.interfaces.tenant_repository_interface import ITenantRepository


class HardDeleteTenantUseCase:
    """
    Permanently deletes a tenant and all related data via CASCADE.
    Requires ENTERPRISE or super-admin privilege — enforced in policy layer.
    """

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
    ) -> None:
        entity = self._tenant_repo.get_by_id(tenant_id)
        if not entity:
            raise TenantNotFoundError(tenant_id)

        with transaction.atomic():

            # Write audit log BEFORE deleting so the FK still resolves
            self._audit_repo.create_log(
                tenant_id=entity.id,  # type: ignore[arg-type]
                user_id=actor_id,
                username=actor_username,
                action="HARD_DELETE",
                module="tenants",
                object_type="Tenant",
                object_id=str(entity.id),
                object_repr=f"{entity.name} ({entity.code})",
                old_values=_entity_to_audit_values(entity),
                ip_address=ip_address,
                user_agent=user_agent,
            )

            self._tenant_repo.delete(tenant_id)
