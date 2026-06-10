"""
Use-cases for Tenant CRUD operations.
Each use-case class has a single public method and
orchestrates domain logic + repositories + audit logging.
"""

from __future__ import annotations

import uuid

from tenants.application.dtos.tenants.tenant_create_dto import TenantCreateDTO
from tenants.application.dtos.tenants.tenant_response_dto import TenantResponseDTO
from tenants.application.usecases.tenants.tenant_usecase import (
    _entity_to_audit_values,
    _entity_to_response,
)
from tenants.domain.entities.tenant_entity import (
    TENANT_PLANS,
    TenantEntity,
)
from tenants.exceptions.exception import TenantAlreadyExistsError
from tenants.repositories.interfaces.tenant_audit_log_repository_interface import (
    ITenantAuditLogRepository,
)
from tenants.repositories.interfaces.tenant_repository_interface import (
    ITenantRepository,
)


class CreateTenantUseCase:
    def __init__(
        self,
        tenant_repo: ITenantRepository,
        audit_repo: ITenantAuditLogRepository,
    ):
        self._tenant_repo = tenant_repo
        self._audit_repo = audit_repo

    def execute(
        self,
        dto: TenantCreateDTO,
        *,
        actor_id: int | None = None,
        actor_username: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TenantResponseDTO:
        code = dto.code.upper().strip()

        if self._tenant_repo.exists_by_code(code):
            raise TenantAlreadyExistsError(code)

        # Apply plan-based defaults if limits not explicitly provided
        plan_def = TENANT_PLANS.get(dto.plan)
        entity = TenantEntity(
            id=None,
            uuid=uuid.uuid4(),
            code=code,
            name=dto.name.strip(),
            plan=dto.plan,
            is_active=dto.is_active,
            currency=dto.currency,
            exchange_rate=dto.exchange_rate,
            default_language=dto.default_language,
            timezone=dto.timezone,
            primary_color=dto.primary_color,
            max_users=dto.max_users if plan_def is None else plan_def.max_users,
            max_branches=(
                dto.max_branches if plan_def is None else plan_def.max_branches
            ),
            max_vehicles=(
                dto.max_vehicles if plan_def is None else plan_def.max_vehicles
            ),
            subscription_started_at=dto.subscription_started_at,
            subscription_expires_at=dto.subscription_expires_at,
            settings=dto.settings,
            domain=dto.domain,
            logo_url=dto.logo_url,
        )

        saved = self._tenant_repo.create(entity)

        self._audit_repo.create_log(
            tenant_id=saved.id,  # type: ignore[arg-type]
            user_id=actor_id,
            username=actor_username,
            action="CREATE",
            module="tenants",
            object_type="Tenant",
            object_id=str(saved.id),
            object_repr=str(saved),
            new_values=_entity_to_audit_values(saved),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return _entity_to_response(saved)
