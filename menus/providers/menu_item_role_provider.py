from __future__ import annotations

from menus.application.usecases.menu_item_roles import (
    CreateMenuItemRoleUseCase,
    DeleteMenuItemRoleUseCase,
    GetMenuItemRoleDetailUseCase,
    HardDeleteMenuItemRoleUseCase,
    ListMenuItemRolesUseCase,
)
from menus.repositories.implement.menu_item_repository_impl import (
    MenuItemRepositoryImpl,
)
from menus.repositories.implement.menu_item_role_repository_impl import (
    MenuItemRoleRepositoryImpl,
)


class MenuItemRoleProvider:
    """
    Static factory instantiating concrete repositories and injecting them into MenuItemRole UseCases.
    """

    @staticmethod
    def _menu_item_role_repo() -> MenuItemRoleRepositoryImpl:
        return MenuItemRoleRepositoryImpl()

    @staticmethod
    def _menu_item_repo() -> MenuItemRepositoryImpl:
        return MenuItemRepositoryImpl()

    @classmethod
    def create_menu_item_role(cls) -> CreateMenuItemRoleUseCase:
        return CreateMenuItemRoleUseCase(
            cls._menu_item_role_repo(), cls._menu_item_repo()
        )

    @classmethod
    def list_menu_item_roles(cls) -> ListMenuItemRolesUseCase:
        return ListMenuItemRolesUseCase(cls._menu_item_role_repo())

    @classmethod
    def delete_menu_item_role(cls) -> DeleteMenuItemRoleUseCase:
        return DeleteMenuItemRoleUseCase(cls._menu_item_role_repo())

    @classmethod
    def hard_delete_menu_item_role(cls) -> HardDeleteMenuItemRoleUseCase:
        return HardDeleteMenuItemRoleUseCase(cls._menu_item_role_repo())

    @classmethod
    def get_menu_item_role_detail(cls) -> GetMenuItemRoleDetailUseCase:
        return GetMenuItemRoleDetailUseCase(cls._menu_item_role_repo())
