"""
Use-case for listing roles.
"""

from __future__ import annotations

from accounts.application.dtos.roles.role_list_query_dto import RoleListQueryDto
from accounts.application.dtos.roles.role_response_dto import RoleResponseDto
from accounts.repositories.interfaces.role_repository_interface import RoleRepository


class ListRolesUseCase:
    """Orchestrates listing roles filtered by search query or active status."""

    def __init__(self, repository: RoleRepository):
        self._repo = repository

    def execute(self, query_dto: RoleListQueryDto) -> tuple[list[RoleResponseDto], int]:
        repo_filters = {}
        if query_dto.is_active is not None:
            repo_filters["is_active"] = query_dto.is_active

        items, total = self._repo.list(
            tenant_id=query_dto.tenant_id,
            filters=repo_filters,
            search=query_dto.search,
            ordering=query_dto.ordering,
            limit=query_dto.limit,
            offset=query_dto.offset,
        )

        return [RoleResponseDto.from_entity(e) for e in items], total
