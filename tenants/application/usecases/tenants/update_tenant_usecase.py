"""
Use-cases for Tenant CRUD operations.
Each use-case class has a single public method and
orchestrates domain logic + repositories + audit logging.
"""
from __future__ import annotations

from tenants.application.dtos.tenants.tenant_response_dto import TenantResponseDTO
from tenants.application.dtos.tenants.tenant_update_dto import TenantUpdateDTO
from tenants.domain.entities import TENANT_PLANS
from tenants.repositories.interfaces.tenant_repository_interface import ITenantRepository
from tenants.repositories.interfaces.tenant_audit_log_repository_interface import ITenantAuditLogRepository
from tenants.application.usecases.tenants.tenant_usecase import _entity_to_response, _entity_to_audit_values, _compute_changes
from tenants.exceptions.exception import TenantNotFoundError


class UpdateTenantUseCase:
    def __init__(
        self,
        tenant_repo: ITenantRepository,
        audit_repo: ITenantAuditLogRepository,
    ):
        self._tenant_repo = tenant_repo
        self._audit_repo = audit_repo

    def execute(
        self,
        dto: TenantUpdateDTO,
        *,
        actor_id: int | None = None,
        actor_username: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TenantResponseDTO:
        entity = self._tenant_repo.get_by_id(dto.tenant_id)
        if not entity:
            raise TenantNotFoundError(dto.tenant_id)

        old_values = _entity_to_audit_values(entity)

        # Merge only provided fields
        if dto.name is not None:
            entity.name = dto.name.strip()
        if dto.plan is not None:
            entity.plan = dto.plan
            plan_def = TENANT_PLANS.get(dto.plan)
            if plan_def:
                entity.max_users = plan_def.max_users
                entity.max_branches = plan_def.max_branches
                entity.max_vehicles = plan_def.max_vehicles
        if dto.currency is not None:
            entity.currency = dto.currency
        if dto.exchange_rate is not None:
            entity.exchange_rate = dto.exchange_rate
        if dto.default_language is not None:
            entity.default_language = dto.default_language
        if dto.timezone is not None:
            entity.timezone = dto.timezone
        if dto.primary_color is not None:
            entity.primary_color = dto.primary_color
        if dto.max_users is not None:
            entity.max_users = dto.max_users
        if dto.max_branches is not None:
            entity.max_branches = dto.max_branches
        if dto.max_vehicles is not None:
            entity.max_vehicles = dto.max_vehicles
        if dto.subscription_started_at is not None:
            entity.subscription_started_at = dto.subscription_started_at
        if dto.subscription_expires_at is not None:
            entity.subscription_expires_at = dto.subscription_expires_at
        if dto.settings is not None:
            entity.settings = dto.settings
        if dto.domain is not None:
            entity.domain = dto.domain
        if dto.logo_url is not None:
            entity.logo_url = dto.logo_url

        saved = self._tenant_repo.update(entity)
        new_values = _entity_to_audit_values(saved)

        self._audit_repo.create_log(
            tenant_id=saved.id,  # type: ignore[arg-type]
            user_id=actor_id,
            username=actor_username,
            action="UPDATE",
            module="tenants",
            object_type="Tenant",
            object_id=str(saved.id),
            object_repr=str(saved),
            old_values=old_values,
            new_values=new_values,
            changes=_compute_changes(old_values, new_values),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return _entity_to_response(saved)