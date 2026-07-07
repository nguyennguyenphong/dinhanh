from abc import ABC, abstractmethod
from typing import Optional, List

from menus.domain.entities.menu_item_role_entity import MenuItemRoleEntity


class IMenuItemRoleRepository(ABC):
    """Abstract interface for MenuItemRole data access."""

    @abstractmethod
    def get_by_id(self, pk: int) -> Optional[MenuItemRoleEntity]:
        pass

    @abstractmethod
    def get_by_uuid(self, pk_uuid: str) -> Optional[MenuItemRoleEntity]:
        pass

    @abstractmethod
    def create(self, **kwargs) -> MenuItemRoleEntity:
        pass

    @abstractmethod
    def delete(self, entity: MenuItemRoleEntity) -> None:
        pass

    @abstractmethod
    def hard_delete(self, entity: MenuItemRoleEntity) -> None:
        pass

    @abstractmethod
    def list(
        self,
        *,
        tenant_id: int,
        menu_item_id: Optional[int] = None,
        role_id: Optional[int] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[List[MenuItemRoleEntity], int]:
        pass

    @abstractmethod
    def exists(self, menu_item_id: int, role_id: int) -> bool:
        pass
