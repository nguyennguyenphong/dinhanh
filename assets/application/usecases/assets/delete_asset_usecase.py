from __future__ import annotations

from assets.repositories.interfaces.asset_repository_interface import IAssetRepository


class DeleteAssetUseCase:

    def __init__(self, repo: IAssetRepository):
        self._repo = repo

    def execute(self, asset_id: int) -> None:
        entity = self._repo.get_by_id(asset_id)
        if not entity:
            raise ValueError(f"Asset with id {asset_id} not found.")
        self._repo.delete(asset_id)
