from __future__ import annotations

from assets.repositories.interfaces.asset_category_repository_interface import IAssetCategoryRepository


class HardDeleteAssetCategoryUseCase:

    def __init__(self, repo: IAssetCategoryRepository):
        self._repo = repo

    def execute(self, category_id: int) -> None:
        self._repo.hard_delete(category_id)
