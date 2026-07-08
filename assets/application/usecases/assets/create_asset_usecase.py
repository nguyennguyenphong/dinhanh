from __future__ import annotations

from assets.application.dtos.assets.asset_dtos import AssetCreateDto, AssetResponseDto
from assets.application.usecases.assets.helper_mapping import entity_to_response
from assets.domain.entities.asset_entity import AssetEntity
from assets.repositories.interfaces.asset_repository_interface import IAssetRepository


class CreateAssetUseCase:

    def __init__(self, repo: IAssetRepository):
        self._repo = repo

    def execute(self, dto: AssetCreateDto) -> AssetResponseDto:
        normalized_code = dto.code.strip().upper()
        if self._repo.exists_by_code(tenant_id=dto.tenant_id, code=normalized_code):
            raise ValueError(
                f"Asset with code {normalized_code} already exists for this tenant."
            )

        # Business check: if current value is not set, set it equal to purchase price
        curr_val = (
            dto.current_value if dto.current_value is not None else dto.purchase_price
        )

        entity = AssetEntity(
            id=None,
            tenant_id=dto.tenant_id,
            category_id=dto.category_id,
            branch_id=dto.branch_id,
            assigned_to_id=dto.assigned_to_id,
            code=normalized_code,
            name=dto.name.strip(),
            serial_number=dto.serial_number.strip() if dto.serial_number else None,
            purchase_date=dto.purchase_date,
            purchase_price=dto.purchase_price,
            depreciation_rate=dto.depreciation_rate,
            current_value=curr_val,
            warranty_expiry=dto.warranty_expiry,
            status=dto.status,
            notes=dto.notes,
        )

        saved = self._repo.create(entity)
        return entity_to_response(saved)
