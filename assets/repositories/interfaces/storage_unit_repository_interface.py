from __future__ import annotations

from abc import ABC, abstractmethod

from assets.domain.entities.storage_unit_entity import StorageUnitEntity


class IStorageUnitRepository(ABC):

    @abstractmethod
    def get_by_id(self, storage_unit_id: int) -> StorageUnitEntity | None:
        pass

    @abstractmethod
    def list(
        self,
        *,
        tenant_id: int,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[StorageUnitEntity], int]:
        pass

    @abstractmethod
    def create(self, entity: StorageUnitEntity) -> StorageUnitEntity:
        pass

    @abstractmethod
    def update(self, entity: StorageUnitEntity) -> StorageUnitEntity:
        pass

    @abstractmethod
    def delete(self, storage_unit_id: int) -> None:
        pass

    @abstractmethod
    def exists_by_code(self, tenant_id: int, code: str, exclude_id: int | None = None) -> bool:
        pass
