from __future__ import annotations

from typing import Any

from assets.domain.entities.storage_unit_entity import StorageUnitEntity
from assets.repositories.interfaces.storage_unit_repository_interface import (
    IStorageUnitRepository,
)


def _model_to_entity(obj: Any) -> StorageUnitEntity:
    return StorageUnitEntity(
        id=obj.pk,
        tenant_id=obj.tenant_id,
        branch_id=obj.branch_id,
        code=obj.code,
        name=obj.name,
        description=obj.description,
        created_at=obj.created_at,
        updated_at=obj.updated_at,
    )


class StorageUnitRepositoryImpl(IStorageUnitRepository):

    @property
    def _qs(self):
        from assets.models import StorageUnit
        return StorageUnit.objects

    def get_by_id(self, storage_unit_id: int) -> StorageUnitEntity | None:
        obj = self._qs.filter(pk=storage_unit_id).first()
        return _model_to_entity(obj) if obj else None

    def list(
        self,
        *,
        tenant_id: int,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[StorageUnitEntity], int]:
        qs = self._qs.filter(tenant_id=tenant_id)
        if search:
            qs = qs.filter(name__icontains=search) | qs.filter(code__icontains=search)
        total = qs.count()
        results = qs[offset : offset + limit]
        return [_model_to_entity(r) for r in results], total

    def create(self, entity: StorageUnitEntity) -> StorageUnitEntity:
        from assets.models import StorageUnit
        obj = StorageUnit.objects.create(
            tenant_id=entity.tenant_id,
            branch_id=entity.branch_id,
            code=entity.code,
            name=entity.name,
            description=entity.description,
        )
        return _model_to_entity(obj)

    def update(self, entity: StorageUnitEntity) -> StorageUnitEntity:
        obj = self._qs.filter(pk=entity.id).first()
        if not obj:
            raise ValueError(f"StorageUnit with id {entity.id} does not exist.")
        obj.branch_id = entity.branch_id
        obj.code = entity.code
        obj.name = entity.name
        obj.description = entity.description
        obj.save()
        return _model_to_entity(obj)

    def delete(self, storage_unit_id: int) -> None:
        self._qs.filter(pk=storage_unit_id).delete()

    def exists_by_code(self, tenant_id: int, code: str, exclude_id: int | None = None) -> bool:
        qs = self._qs.filter(tenant_id=tenant_id, code__iexact=code.strip())
        if exclude_id:
            qs = qs.exclude(pk=exclude_id)
        return qs.exists()
