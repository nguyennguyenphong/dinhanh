"""
Use-cases for Tenant CRUD operations.
Each use-case class has a single public method and
orchestrates domain logic + repositories + audit logging.
"""
from __future__ import annotations
from typing import Any

from tenants.application.dtos.tenants.tenant_list_query_dto import TenantListQueryDTO
from tenants.repositories.interfaces.tenant_repository_interface import ITenantRepository
from tenants.application.dtos.tenants.tenant_response_dto import TenantResponseDTO
from tenants.application.usecases.tenants.tenant_usecase import _entity_to_response



class ListTenantsUseCase:
    def __init__(self, tenant_repo: ITenantRepository):
        self._tenant_repo = tenant_repo

    def execute(
        self, query: TenantListQueryDTO
    ) -> tuple[list[TenantResponseDTO], int]:
        filters: dict[str, Any] = {}
        if query.plan:
            filters["plan"] = query.plan
        if query.is_active is not None:
            filters["is_active"] = query.is_active

        items, total = self._tenant_repo.list(
            filters=filters,
            search=query.search,
            ordering=query.ordering,
            limit=query.limit,
            offset=query.offset,
        )
        return [_entity_to_response(e) for e in items], total