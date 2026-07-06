from abc import ABC, abstractmethod
from typing import Optional

from menus.domain.entities.menu_item_entity import MenuItemEntity


class IMenuItemRepository(ABC):
    """Abstract interface for MenuItem data access."""

    @abstractmethod
    def get_by_id(self, item_id: int) -> Optional[MenuItemEntity]:
        pass

    @abstractmethod
    def get_by_uuid(self, uuid: str) -> Optional[MenuItemEntity]:
        pass

    @abstractmethod
    def get_by_code(self, tenant_id: int, code: str) -> Optional[MenuItemEntity]:
        pass

    @abstractmethod
    def get_all_for_tenant(self, tenant_id: int):
        pass

    @abstractmethod
    def get_for_group(self, group_id: int):
        pass

    @abstractmethod
    def get_root_items(self, tenant_id: int):
        """Return items with no parent."""

    @abstractmethod
    def get_children(self, parent_id: int):
        pass

    @abstractmethod
    def create(self, **kwargs) -> MenuItemEntity:
        pass

    @abstractmethod
    def update(self, item: MenuItemEntity, **kwargs) -> MenuItemEntity:
        pass

    @abstractmethod
    def delete(self, item: MenuItemEntity) -> None:
        pass

    @abstractmethod
    def bulk_reorder(self, tenant_id: int, order_data: list[dict]) -> None:
        """
        Update sort_order for multiple items at once.

        Args:
            tenant_id: Tenant PK
            order_data: list of {'id': int, 'sort_order': int}
        """

    @abstractmethod
    def exists_with_code(
        self, tenant_id: int, code: str, exclude_id: Optional[int] = None
    ) -> bool:
        pass
