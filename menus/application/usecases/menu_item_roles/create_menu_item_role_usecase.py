from accounts.models.roles import Role  # for aggregate boundary check
from menus.application.dtos.menu_item_roles import (
    MenuItemRoleCreateDto,
    MenuItemRoleResponseDto,
)
from menus.repositories.interfaces.menu_item_repository_interface import (
    IMenuItemRepository,
)
from menus.repositories.interfaces.menu_item_role_repository_interface import (
    IMenuItemRoleRepository,
)


class CreateMenuItemRoleUseCase:
    """Handles assignment of a Role to a MenuItem under tenant boundary constraints."""

    def __init__(
        self,
        menu_item_role_repo: IMenuItemRoleRepository,
        menu_item_repo: IMenuItemRepository,
    ):
        self._repo = menu_item_role_repo
        self._menu_item_repo = menu_item_repo

    def execute(self, dto: MenuItemRoleCreateDto) -> MenuItemRoleResponseDto:
        # 1. Fetch menu item and check existence
        menu_item = self._menu_item_repo.get_by_id(dto.menu_item_id)
        if not menu_item:
            raise ValueError("Menu item does not exist.")

        # 2. Fetch role and check existence
        role = Role.objects.filter(pk=dto.role_id).first()
        if not role:
            raise ValueError("Role does not exist.")

        # 3. Tenant alignment check
        if menu_item.tenant_id != role.tenant_id:
            raise ValueError("Menu item and role must belong to the same tenant.")

        # 4. Check if already exists
        if self._repo.exists(dto.menu_item_id, dto.role_id):
            raise ValueError("This role is already assigned to this menu item.")

        entity = self._repo.create(
            menu_item_id=dto.menu_item_id,
            role_id=dto.role_id,
        )

        return MenuItemRoleResponseDto.from_entity(entity)
