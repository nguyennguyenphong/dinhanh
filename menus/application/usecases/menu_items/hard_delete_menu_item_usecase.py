from menus.application.dtos.menu_items import MenuItemDeleteDto
from menus.exceptions import MenuItemNotFoundError
from menus.repositories.interfaces.menu_item_repository_interface import (
    IMenuItemRepository,
)


class HardDeleteMenuItemUseCase:
    """CRITICAL: Force purges a MenuItem record entirely from the DB."""

    def __init__(self, menu_item_repo: IMenuItemRepository):
        self._repo = menu_item_repo

    def execute(self, dto: MenuItemDeleteDto) -> None:
        entity = self._repo.get_by_id(dto.id)
        if not entity or entity.tenant_id != dto.tenant_id:
            raise MenuItemNotFoundError(dto.id)

        self._repo.hard_delete(entity)
