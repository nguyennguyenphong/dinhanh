"""
Use-cases for Tenant CRUD operations.
Each use-case class has a single public method and
orchestrates domain logic + repositories + audit logging.
"""

from __future__ import annotations

from tenants.application.dtos.tenants.tenant_response_dto import TenantResponseDTO
from tenants.application.usecases.tenants.tenant_usecase import _entity_to_response
from tenants.exceptions.exception import TenantNotFoundError
from tenants.repositories.interfaces.tenant_repository_interface import (
    ITenantRepository,
)


class GetTenantUseCase:
    def __init__(self, tenant_repo: ITenantRepository):
        self._tenant_repo = tenant_repo

    def by_id(self, tenant_id: int) -> TenantResponseDTO:
        entity = self._tenant_repo.get_by_id(tenant_id)
        if not entity:
            raise TenantNotFoundError(tenant_id)
        return _entity_to_response(entity)

    def by_uuid(self, uuid_value: str) -> TenantResponseDTO:
        entity = self._tenant_repo.get_by_uuid(uuid_value)
        if not entity:
            raise TenantNotFoundError(uuid_value)
        return _entity_to_response(entity)

    def by_code(self, code: str) -> TenantResponseDTO:
        entity = self._tenant_repo.get_by_code(code)
        if not entity:
            raise TenantNotFoundError(code)
        return _entity_to_response(entity)
