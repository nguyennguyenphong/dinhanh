from __future__ import annotations

from menus.application.dtos.menu_items import (
    MenuItemListQueryDto,
    MenuItemResponseDto,
)
from menus.application.usecases.menu_items.helper_mapping_menu_item_usecase import (
    _entity_to_response,
)
from menus.repositories.interfaces.menu_item_repository_interface import (
    IMenuItemRepository,
)


class ListMenuItemsUseCase:
    """Fetches a paginated, search-filtered chunk of MenuItems for the list UI/API."""

    def __init__(self, menu_item_repo: IMenuItemRepository):
        self._repo = menu_item_repo

    def execute(
        self, query_dto: MenuItemListQueryDto
    ) -> tuple[list[MenuItemResponseDto], int]:

        repo_filters = {}
        if query_dto.is_active is not None:
            repo_filters["is_active"] = query_dto.is_active

        items, total = self._repo.list(
            tenant_id=query_dto.tenant_id,
            group_id=query_dto.group_id,
            parent_id=query_dto.parent_id,
            filters=repo_filters,
            search=query_dto.search,
            ordering=query_dto.ordering,
            limit=query_dto.limit,
            offset=query_dto.offset,
            include_deleted=False,
        )

        return [_entity_to_response(e) for e in items], total
