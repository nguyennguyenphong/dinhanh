from __future__ import annotations

from assets.repositories.interfaces.asset_repository_interface import IAssetRepository


class HardDeleteAssetUseCase:

    def __init__(self, repo: IAssetRepository):
        self._repo = repo

    def execute(self, asset_id: int) -> None:
        self._repo.hard_delete(asset_id)
