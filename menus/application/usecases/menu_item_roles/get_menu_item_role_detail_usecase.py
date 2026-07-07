from menus.application.dtos.menu_item_roles import MenuItemRoleResponseDto
from menus.repositories.interfaces.menu_item_role_repository_interface import (
    IMenuItemRoleRepository,
)


class GetMenuItemRoleDetailUseCase:
    """Retrieves a menu item role assignment by ID."""

    def __init__(self, menu_item_role_repo: IMenuItemRoleRepository):
        self._repo = menu_item_role_repo

    def execute(self, pk: int) -> MenuItemRoleResponseDto:
        entity = self._repo.get_by_id(pk)
        if not entity:
            raise ValueError("Menu item role assignment not found.")
        return MenuItemRoleResponseDto.from_entity(entity)
