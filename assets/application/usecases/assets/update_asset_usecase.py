from __future__ import annotations

from assets.application.dtos.assets.asset_dtos import AssetResponseDto, AssetUpdateDto
from assets.application.usecases.assets.helper_mapping import entity_to_response
from assets.repositories.interfaces.asset_repository_interface import IAssetRepository


class UpdateAssetUseCase:

    def __init__(self, repo: IAssetRepository):
        self._repo = repo

    def execute(self, dto: AssetUpdateDto) -> AssetResponseDto:
        entity = self._repo.get_by_id(dto.id)
        if not entity:
            raise ValueError(f"Asset with id {dto.id} not found.")

        normalized_code = dto.code.strip().upper()
        if self._repo.exists_by_code(
            tenant_id=entity.tenant_id, code=normalized_code, exclude_id=dto.id
        ):
            raise ValueError(
                f"Asset with code {normalized_code} already exists for this tenant."
            )

        # Update properties
        entity.category_id = dto.category_id
        entity.branch_id = dto.branch_id
        entity.assigned_to_id = dto.assigned_to_id
        entity.code = normalized_code
        entity.name = dto.name.strip()
        entity.serial_number = dto.serial_number.strip() if dto.serial_number else None
        entity.purchase_date = dto.purchase_date
        entity.purchase_price = dto.purchase_price
        entity.depreciation_rate = dto.depreciation_rate
        entity.current_value = (
            dto.current_value if dto.current_value is not None else dto.purchase_price
        )
        entity.warranty_expiry = dto.warranty_expiry
        entity.status = dto.status
        entity.notes = dto.notes

        saved = self._repo.update(entity)
        return entity_to_response(saved)
