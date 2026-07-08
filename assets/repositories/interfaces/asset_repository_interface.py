from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from assets.domain.entities.asset_entity import AssetEntity


class IAssetRepository(ABC):

    @abstractmethod
    def get_by_id(self, asset_id: int) -> AssetEntity | None:
        pass

    @abstractmethod
    def get_by_uuid(self, uuid: str) -> AssetEntity | None:
        pass

    @abstractmethod
    def list(
        self,
        *,
        tenant_id: int,
        filters: dict[str, Any] | None = None,
        search: str | None = None,
        ordering: list[str] | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[AssetEntity], int]:
        pass

    @abstractmethod
    def create(self, entity: AssetEntity) -> AssetEntity:
        pass

    @abstractmethod
    def update(self, entity: AssetEntity) -> AssetEntity:
        pass

    @abstractmethod
    def delete(self, asset_id: int) -> None:
        pass

    @abstractmethod
    def exists_by_code(
        self, tenant_id: int, code: str, exclude_id: int | None = None
    ) -> bool:
        pass
