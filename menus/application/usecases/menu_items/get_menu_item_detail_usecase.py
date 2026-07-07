from menus.application.dtos.menu_items import MenuItemDetailDto
from menus.exceptions import MenuItemNotFoundError
from menus.repositories.interfaces.menu_item_repository_interface import (
    IMenuItemRepository,
)


class GetMenuItemDetailUseCase:
    """Retrieves MenuItem details by ID."""

    def __init__(self, menu_item_repo: IMenuItemRepository):
        self._repo = menu_item_repo

    def execute(self, item_id: int) -> MenuItemDetailDto:
        entity = self._repo.get_by_id(item_id)
        if not entity:
            raise MenuItemNotFoundError(item_id)

        return MenuItemDetailDto.from_entity(entity)
