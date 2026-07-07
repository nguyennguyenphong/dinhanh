from __future__ import annotations

from menus.application.usecases.menu_items import (
    CreateMenuItemUseCase,
    UpdateMenuItemUseCase,
    GetMenuItemDetailUseCase,
    ListMenuItemsUseCase,
    DeleteMenuItemUseCase,
    HardDeleteMenuItemUseCase,
)
from menus.repositories.implement.menu_item_repository_impl import MenuItemRepositoryImpl


class MenuItemProvider:
    """
    Static factory — instantiates concrete repositories and injects them into use-cases.
    Allows swapping underlying data access layers cleanly without modifying application logic.
    """

    @staticmethod
    def _menu_item_repo() -> MenuItemRepositoryImpl:
        """Returns the concrete Django ORM implementation for MenuItem repository."""
        return MenuItemRepositoryImpl()

    @classmethod
    def create_menu_item(cls) -> CreateMenuItemUseCase:
        """Factory for generating a new MenuItem creation flow instance."""
        return CreateMenuItemUseCase(cls._menu_item_repo())

    @classmethod
    def update_menu_item(cls) -> UpdateMenuItemUseCase:
        """Factory for generating an existing MenuItem update flow instance."""
        return UpdateMenuItemUseCase(cls._menu_item_repo())

    @classmethod
    def get_menu_item_detail(cls) -> GetMenuItemDetailUseCase:
        """Factory for generating a specific MenuItem detailed query flow instance."""
        return GetMenuItemDetailUseCase(cls._menu_item_repo())

    @classmethod
    def list_menu_items(cls) -> ListMenuItemsUseCase:
        """Factory for generating a paginated listing and filtering search flow instance."""
        return ListMenuItemsUseCase(cls._menu_item_repo())

    @classmethod
    def delete_menu_item(cls) -> DeleteMenuItemUseCase:
        """Factory for generating a safe records logical deletion flow instance."""
        return DeleteMenuItemUseCase(cls._menu_item_repo())

    @classmethod
    def hard_delete_menu_item(cls) -> HardDeleteMenuItemUseCase:
        """Factory for permanently stripping data records out of physical tables."""
        return HardDeleteMenuItemUseCase(cls._menu_item_repo())
