from __future__ import annotations

from assets.application.dtos.assets.asset_dtos import AssetResponseDto
from assets.application.usecases.assets.helper_mapping import entity_to_response
from assets.repositories.interfaces.asset_repository_interface import IAssetRepository


class GetAssetDetailUseCase:

    def __init__(self, repo: IAssetRepository):
        self._repo = repo

    def execute(self, asset_id: int) -> AssetResponseDto | None:
        entity = self._repo.get_by_id(asset_id)
        return entity_to_response(entity) if entity else None

    def execute_by_uuid(self, uuid_str: str) -> AssetResponseDto | None:
        entity = self._repo.get_by_uuid(uuid_str)
        return entity_to_response(entity) if entity else None
