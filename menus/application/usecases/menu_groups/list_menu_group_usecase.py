"""
Use-cases for MenuGroup operations.
Each use-case class has a single public method and
orchestrates domain logic, repositories, and business rules validation.
"""

from __future__ import annotations

from typing import Any

from menus.application.dtos.menu_groups import MenuGroupListDto
from menus.repositories.interfaces import IMenuGroupRepository


class ListMenuGroupsUseCase:
    """Fetches a paginated, search-filtered chunk of MenuGroups for the main list UI."""

    def __init__(self, menu_group_repo: IMenuGroupRepository):
        self._repo = menu_group_repo

    def execute(
        self,
        *,
        tenant_id: int,
        search: str | None = None,
        filters: dict[str, Any] | None = None,
        ordering: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> MenuGroupListDto:
        entities, total_count = self._repo.list(
            tenant_id=tenant_id,
            filters=filters,
            search=search,
            ordering=ordering,
            limit=limit,
            offset=offset,
            include_deleted=include_deleted,
        )

        return MenuGroupListDto.from_entities(
            entities=entities,
            total_count=total_count,
            limit=limit,
            offset=offset,
        )