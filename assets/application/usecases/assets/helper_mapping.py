from assets.application.dtos.assets.asset_dtos import AssetResponseDto
from assets.domain.entities.asset_entity import AssetEntity


def entity_to_response(entity: AssetEntity) -> AssetResponseDto:
    return AssetResponseDto(
        id=entity.id,
        tenant_id=entity.tenant_id,
        category_id=entity.category_id,
        branch_id=entity.branch_id,
        assigned_to_id=entity.assigned_to_id,
        code=entity.code,
        name=entity.name,
        serial_number=entity.serial_number,
        purchase_date=entity.purchase_date,
        purchase_price=entity.purchase_price,
        depreciation_rate=entity.depreciation_rate,
        current_value=entity.current_value,
        warranty_expiry=entity.warranty_expiry,
        status=entity.status,
        notes=entity.notes,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )
