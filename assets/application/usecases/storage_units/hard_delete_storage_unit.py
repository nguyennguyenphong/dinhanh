from __future__ import annotations

from assets.repositories.interfaces.storage_unit_repository_interface import IStorageUnitRepository


class HardDeleteStorageUnitUseCase:

    def __init__(self, repo: IStorageUnitRepository):
        self._repo = repo

    def execute(self, storage_unit_id: int) -> None:
        self._repo.hard_delete(storage_unit_id)
