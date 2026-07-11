from __future__ import annotations

from assets.repositories.interfaces.asset_category_repository_interface import (
    IAssetCategoryRepository,
)


class SoftDeleteAssetCategoryUseCase:

    def __init__(self, repo: IAssetCategoryRepository):
        self._repo = repo

    def execute(self, category_id: int) -> None:
        entity = self._repo.get_by_id(category_id)
        if not entity:
            raise ValueError(f"AssetCategory with id {category_id} not found.")
        self._repo.delete(category_id)
