"""
Dependency injection provider for the MenuGroup bounded context.

Usage:
    from menus.providers.menu_group_provider import MenuGroupProvider

    use_case = MenuGroupProvider.create_menu_group_use_case()
    result = use_case.execute(dto)
"""

from __future__ import annotations

from menus.application.usecases.menu_groups import (
    CreateMenuGroupUseCase,
    GetMenuGroupDetailUseCase,
    HardDeleteMenuGroupUseCase,
    ListMenuGroupsUseCase,
    SoftDeleteMenuGroupUseCase,
    UpdateMenuGroupUseCase,
)
from menus.repositories.implement import MenuGroupRepositoryImpl


class MenuGroupProvider:
    """
    Static factory — instantiates concrete repositories and injects them into use-cases.
    Allows swapping underlying data access layers cleanly without modifying application logic.
    """

    # ------------------------------------------------------------------ #
    # Shared repository instances (stateless, safe to share per request) #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _menu_group_repo() -> MenuGroupRepositoryImpl:
        """Returns the concrete Django ORM implementation for MenuGroup repository."""
        return MenuGroupRepositoryImpl()

    # ------------------------------------------------------------------ #
    # Use-case factories                                                 #
    # ------------------------------------------------------------------ #

    @classmethod
    def create_menu_group_use_case(cls) -> CreateMenuGroupUseCase:
        """Factory for generating a new MenuGroup creation flow instance."""
        return CreateMenuGroupUseCase(cls._menu_group_repo())

    @classmethod
    def update_menu_group_use_case(cls) -> UpdateMenuGroupUseCase:
        """Factory for generating an existing MenuGroup update flow instance."""
        return UpdateMenuGroupUseCase(cls._menu_group_repo())

    @classmethod
    def get_menu_group_detail_use_case(cls) -> GetMenuGroupDetailUseCase:
        """Factory for generating a specific MenuGroup detailed query flow instance."""
        return GetMenuGroupDetailUseCase(cls._menu_group_repo())

    @classmethod
    def list_menu_groups_use_case(cls) -> ListMenuGroupsUseCase:
        """Factory for generating a paginated listing and filtering search flow instance."""
        return ListMenuGroupsUseCase(cls._menu_group_repo())

    @classmethod
    def soft_delete_menu_group_use_case(cls) -> SoftDeleteMenuGroupUseCase:
        """Factory for generating a safe records logical deletion flow instance."""
        return SoftDeleteMenuGroupUseCase(cls._menu_group_repo())

    @classmethod
    def hard_delete_menu_group_use_case(cls) -> HardDeleteMenuGroupUseCase:
        """Factory for permanently stripping data records out of physical tables."""
        return HardDeleteMenuGroupUseCase(cls._menu_group_repo())