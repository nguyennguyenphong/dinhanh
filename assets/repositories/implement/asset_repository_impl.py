from __future__ import annotations

from typing import Any

from django.db.models import Q

from assets.domain.entities.asset_entity import AssetEntity
from assets.repositories.interfaces.asset_repository_interface import IAssetRepository


def _model_to_entity(obj: Any) -> AssetEntity:
    return AssetEntity(
        id=obj.pk,
        tenant_id=obj.tenant_id,
        category_id=obj.category_id,
        branch_id=obj.branch_id,
        assigned_to_id=obj.assigned_to_id,
        code=obj.code,
        name=obj.name,
        serial_number=obj.serial_number,
        purchase_date=obj.purchase_date,
        purchase_price=obj.purchase_price,
        depreciation_rate=obj.depreciation_rate,
        current_value=obj.current_value,
        warranty_expiry=obj.warranty_expiry,
        status=obj.status,
        notes=obj.notes,
        created_at=obj.created_at,
        updated_at=obj.updated_at,
    )


class AssetRepositoryImpl(IAssetRepository):

    @property
    def _qs(self):
        from assets.models import Asset

        return Asset.objects

    def get_by_id(self, asset_id: int) -> AssetEntity | None:
        obj = self._qs.filter(pk=asset_id).first()
        return _model_to_entity(obj) if obj else None

    def get_by_uuid(self, uuid_str: str) -> AssetEntity | None:
        obj = self._qs.filter(uuid=uuid_str).first()
        return _model_to_entity(obj) if obj else None

    def list(
        self,
        *,
        tenant_id: int,
        filters: dict[str, Any] | None = None,
        search: str | None = None,
        ordering: list[str] | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[AssetEntity], int]:
        qs = self._qs.filter(tenant_id=tenant_id)

        if filters:
            if "status" in filters and filters["status"]:
                qs = qs.filter(status=filters["status"])
            if "category_id" in filters and filters["category_id"]:
                qs = qs.filter(category_id=filters["category_id"])
            if "branch_id" in filters and filters["branch_id"]:
                qs = qs.filter(branch_id=filters["branch_id"])

        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(code__icontains=search)
                | Q(serial_number__icontains=search)
            )

        if ordering:
            qs = qs.order_by(*ordering)
        else:
            qs = qs.order_by("-created_at")

        total = qs.count()
        results = qs[offset : offset + limit]
        return [_model_to_entity(r) for r in results], total

    def create(self, entity: AssetEntity) -> AssetEntity:
        from assets.models import Asset

        obj = Asset.objects.create(
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
        )
        return _model_to_entity(obj)

    def update(self, entity: AssetEntity) -> AssetEntity:
        obj = self._qs.filter(pk=entity.id).first()
        if not obj:
            raise ValueError(f"Asset with id {entity.id} does not exist.")
        obj.category_id = entity.category_id
        obj.branch_id = entity.branch_id
        obj.assigned_to_id = entity.assigned_to_id
        obj.code = entity.code
        obj.name = entity.name
        obj.serial_number = entity.serial_number
        obj.purchase_date = entity.purchase_date
        obj.purchase_price = entity.purchase_price
        obj.depreciation_rate = entity.depreciation_rate
        obj.current_value = entity.current_value
        obj.warranty_expiry = entity.warranty_expiry
        obj.status = entity.status
        obj.notes = entity.notes
        obj.save()
        return _model_to_entity(obj)

    def delete(self, asset_id: int) -> None:
        self._qs.filter(pk=asset_id).delete()

    def exists_by_code(
        self, tenant_id: int, code: str, exclude_id: int | None = None
    ) -> bool:
        qs = self._qs.filter(tenant_id=tenant_id, code__iexact=code.strip())
        if exclude_id:
            qs = qs.exclude(pk=exclude_id)
        return qs.exists()
