from __future__ import annotations

from assets.repositories.interfaces.storage_unit_repository_interface import IStorageUnitRepository


class SoftDeleteStorageUnitUseCase:

    def __init__(self, repo: IStorageUnitRepository):
        self._repo = repo

    def execute(self, storage_unit_id: int) -> None:
        entity = self._repo.get_by_id(storage_unit_id)
        if not entity:
            raise ValueError(f"StorageUnit with id {storage_unit_id} not found.")
        self._repo.delete(storage_unit_id)
