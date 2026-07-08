from __future__ import annotations

from abc import ABC, abstractmethod

from assets.domain.entities.asset_category_entity import AssetCategoryEntity


class IAssetCategoryRepository(ABC):

    @abstractmethod
    def get_by_id(self, category_id: int) -> AssetCategoryEntity | None:
        pass

    @abstractmethod
    def list(
        self,
        *,
        tenant_id: int,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[AssetCategoryEntity], int]:
        pass

    @abstractmethod
    def create(self, entity: AssetCategoryEntity) -> AssetCategoryEntity:
        pass

    @abstractmethod
    def update(self, entity: AssetCategoryEntity) -> AssetCategoryEntity:
        pass

    @abstractmethod
    def delete(self, category_id: int) -> None:
        pass

    @abstractmethod
    def exists_by_name(self, tenant_id: int, name: str, exclude_id: int | None = None) -> bool:
        pass
