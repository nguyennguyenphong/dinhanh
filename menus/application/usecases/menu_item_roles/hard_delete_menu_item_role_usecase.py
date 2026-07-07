from menus.application.dtos.menu_item_roles import MenuItemRoleDeleteDto
from menus.repositories.interfaces.menu_item_role_repository_interface import (
    IMenuItemRoleRepository,
)


class HardDeleteMenuItemRoleUseCase:
    """Hard deletes a menu item role assignment."""

    def __init__(self, menu_item_role_repo: IMenuItemRoleRepository):
        self._repo = menu_item_role_repo

    def execute(self, dto: MenuItemRoleDeleteDto) -> None:
        entity = self._repo.get_by_id(dto.id)
        if not entity or entity.tenant_id != dto.tenant_id:
            raise ValueError("Menu item role assignment not found.")

        self._repo.hard_delete(entity)
