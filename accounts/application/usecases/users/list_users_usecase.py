"""
Use-case for listing users with pagination, search and active filters.
"""

from __future__ import annotations

from accounts.application.dtos.users.user_list_query_dto import UserListQueryDto
from accounts.application.dtos.users.user_response_dto import UserResponseDto
from accounts.repositories.interfaces.user_repository_interface import UserRepository


class ListUsersUseCase:
    """Orchestrates listing users filtered by search query or active status."""

    def __init__(self, repository: UserRepository):
        self._repo = repository

    def execute(self, query_dto: UserListQueryDto) -> tuple[list[UserResponseDto], int]:
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

        return [UserResponseDto.from_entity(e) for e in items], total
