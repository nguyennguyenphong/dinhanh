from __future__ import annotations

import uuid
from typing import Any

from accounts.domain.entities.permission_entity import PermissionEntity
from accounts.repositories.interfaces.permission_repository_interface import (
    PermissionRepository,
)


def _model_to_entity(obj: Any) -> PermissionEntity:
    return PermissionEntity(
        id=obj.pk,
        uuid=obj.uuid,
        tenant_id=obj.tenant_id,
        name=obj.name,
        codename=obj.codename,
        module=obj.module,
        action=obj.action,
        parent_id=obj.parent_id,
        is_system=obj.is_system,
        is_active=obj.is_active,
        created_at=obj.created_at,
        updated_at=obj.updated_at,
    )


class PermissionRepositoryImpl(PermissionRepository):

    @property
    def _model(self):
        from accounts.models.permissions import Permission

        return Permission

    def save(self, entity: PermissionEntity) -> PermissionEntity:
        if entity.id:
            obj = self._model.all_objects.filter(pk=entity.id).first()
            if not obj:
                raise ValueError("Permission not found to update")
            obj.name = entity.name.strip()
            obj.codename = entity.codename.strip().lower()
            obj.module = entity.module.strip()
            obj.action = entity.action.strip()
            obj.parent_id = entity.parent_id
            obj.is_active = entity.is_active
            obj.save()
        else:
            obj = self._model(
                uuid=entity.uuid,
                tenant_id=entity.tenant_id,
                name=entity.name.strip(),
                codename=entity.codename.strip().lower(),
                module=entity.module.strip(),
                action=entity.action.strip(),
                parent_id=entity.parent_id,
                is_system=entity.is_system,
                is_active=entity.is_active,
            )
            obj.save()

        return _model_to_entity(obj)

    def find_by_uuid(self, permission_uuid: uuid.UUID) -> PermissionEntity | None:
        obj = self._model.all_objects.filter(uuid=permission_uuid).first()
        return _model_to_entity(obj) if obj else None

    def exists_by_codename(
        self, tenant_id: int, codename: str, exclude_id: int | None = None
    ) -> bool:
        qs = self._model.all_objects.filter(
            tenant_id=tenant_id, codename=codename.strip().lower()
        )
        if exclude_id:
            qs = qs.exclude(pk=exclude_id)
        return qs.exists()

    def delete(self, permission_uuid: uuid.UUID) -> bool:
        obj = self._model.all_objects.filter(uuid=permission_uuid).first()
        if not obj:
            return False
        obj.delete()  # soft delete via safedelete
        return True

    def hard_delete(self, permission_uuid: uuid.UUID) -> bool:
        obj = self._model.all_objects.filter(uuid=permission_uuid).first()
        if not obj:
            return False
        from safedelete.models import HARD_DELETE

        obj.delete(force_policy=HARD_DELETE)
        return True

    def list(
        self,
        *,
        tenant_id: int,
        filters: dict[str, Any] | None = None,
        search: str | None = None,
        ordering: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[PermissionEntity], int]:
        from django.db.models import Q

        qs = self._model.objects.filter(tenant_id=tenant_id)

        if filters:
            if filters.get("is_active") is not None:
                qs = qs.filter(is_active=filters["is_active"])

        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(codename__icontains=search)
                | Q(module__icontains=search)
                | Q(action__icontains=search)
            )

        total = qs.count()

        if ordering:
            qs = qs.order_by(*ordering)
        else:
            qs = qs.order_by("-created_at")

        items = [_model_to_entity(obj) for obj in qs[offset : offset + limit]]
        return items, total
