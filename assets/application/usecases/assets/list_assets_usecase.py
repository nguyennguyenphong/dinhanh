from __future__ import annotations

from typing import Any

from assets.application.dtos.assets.asset_dtos import AssetResponseDto
from assets.application.usecases.assets.helper_mapping import entity_to_response
from assets.repositories.interfaces.asset_repository_interface import IAssetRepository


class ListAssetsUseCase:

    def __init__(self, repo: IAssetRepository):
        self._repo = repo

    def execute(
        self,
        tenant_id: int,
        filters: dict[str, Any] | None = None,
        search: str | None = None,
        ordering: list[str] | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[AssetResponseDto], int]:
        entities, total = self._repo.list(
            tenant_id=tenant_id,
            filters=filters,
            search=search,
            ordering=ordering,
            limit=limit,
            offset=offset,
        )
        return [entity_to_response(e) for e in entities], total
