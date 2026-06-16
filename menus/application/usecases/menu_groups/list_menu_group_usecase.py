"""
Use-cases for MenuGroup operations.
Each use-case class has a single public method and
orchestrates domain logic, repositories, and business rules validation.
"""

from __future__ import annotations

from menus.application.dtos.menu_groups import (
    MenuGroupListQueryDto,
    MenuGroupResponseDto,
)
from menus.application.usecases.menu_groups.helper_mapping_menu_group_usecase import (
    _entity_to_response,
)
from menus.repositories.interfaces import IMenuGroupRepository


class ListMenuGroupsUseCase:
    """Fetches a paginated, search-filtered chunk of MenuGroups for the main list UI."""

    def __init__(self, menu_group_repo: IMenuGroupRepository):
        self._repo = menu_group_repo

    def execute(
        self, query_dto: MenuGroupListQueryDto
    ) -> tuple[list[MenuGroupResponseDto], int]:

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
            include_deleted=False,
        )

        return [_entity_to_response(e) for e in items], total
