from __future__ import annotations

from typing import Any

from assets.domain.entities.asset_category_entity import AssetCategoryEntity
from assets.repositories.interfaces.asset_category_repository_interface import (
    IAssetCategoryRepository,
)


def _model_to_entity(obj: Any) -> AssetCategoryEntity:
    return AssetCategoryEntity(
        id=obj.pk,
        tenant_id=obj.tenant_id,
        name=obj.name,
        created_at=obj.created_at,
        updated_at=obj.updated_at,
    )


class AssetCategoryRepositoryImpl(IAssetCategoryRepository):

    @property
    def _qs(self):
        from assets.models import AssetCategory
        return AssetCategory.objects

    def get_by_id(self, category_id: int) -> AssetCategoryEntity | None:
        obj = self._qs.filter(pk=category_id).first()
        return _model_to_entity(obj) if obj else None

    def list(
        self,
        *,
        tenant_id: int,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[AssetCategoryEntity], int]:
        qs = self._qs.filter(tenant_id=tenant_id)
        if search:
            qs = qs.filter(name__icontains=search)
        total = qs.count()
        results = qs[offset : offset + limit]
        return [_model_to_entity(r) for r in results], total

    def create(self, entity: AssetCategoryEntity) -> AssetCategoryEntity:
        from assets.models import AssetCategory
        obj = AssetCategory.objects.create(
            tenant_id=entity.tenant_id,
            name=entity.name,
        )
        return _model_to_entity(obj)

    def update(self, entity: AssetCategoryEntity) -> AssetCategoryEntity:
        obj = self._qs.filter(pk=entity.id).first()
        if not obj:
            raise ValueError(f"AssetCategory with id {entity.id} does not exist.")
        obj.name = entity.name
        obj.save()
        return _model_to_entity(obj)

    def delete(self, category_id: int) -> None:
        self._qs.filter(pk=category_id).delete()

    def exists_by_name(self, tenant_id: int, name: str, exclude_id: int | None = None) -> bool:
        qs = self._qs.filter(tenant_id=tenant_id, name__iexact=name.strip())
        if exclude_id:
            qs = qs.exclude(pk=exclude_id)
        return qs.exists()
