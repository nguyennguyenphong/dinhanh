from menus.application.dtos.menu_item_roles import (
    MenuItemRoleListQueryDto,
    MenuItemRoleResponseDto,
)
from menus.repositories.interfaces.menu_item_role_repository_interface import (
    IMenuItemRoleRepository,
)


class ListMenuItemRolesUseCase:
    """Lists menu item roles."""

    def __init__(self, menu_item_role_repo: IMenuItemRoleRepository):
        self._repo = menu_item_role_repo

    def execute(
        self, query_dto: MenuItemRoleListQueryDto
    ) -> tuple[list[MenuItemRoleResponseDto], int]:
        items, total = self._repo.list(
            tenant_id=query_dto.tenant_id,
            menu_item_id=query_dto.menu_item_id,
            role_id=query_dto.role_id,
            limit=query_dto.limit,
            offset=query_dto.offset,
        )

        return [MenuItemRoleResponseDto.from_entity(e) for e in items], total
