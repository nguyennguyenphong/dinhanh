"""
Use-case for listing permissions.
"""

from __future__ import annotations

from accounts.application.dtos.permissions.permission_list_query_dto import PermissionListQueryDto
from accounts.application.dtos.permissions.permission_response_dto import PermissionResponseDto
from accounts.repositories.interfaces.permission_repository_interface import PermissionRepository


class ListPermissionsUseCase:
    """Orchestrates listing permissions filtered by search query or active status."""

    def __init__(self, repository: PermissionRepository):
        self._repo = repository

    def execute(self, query_dto: PermissionListQueryDto) -> tuple[list[PermissionResponseDto], int]:
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

        return [PermissionResponseDto.from_entity(e) for e in items], total
