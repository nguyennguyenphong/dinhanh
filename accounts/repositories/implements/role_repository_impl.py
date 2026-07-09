from __future__ import annotations

import uuid
from typing import Any

from accounts.domain.entities.role_entity import RoleEntity
from accounts.repositories.interfaces.role_repository_interface import RoleRepository


def _model_to_entity(obj: Any) -> RoleEntity:
    return RoleEntity(
        id=obj.pk,
        uuid=obj.uuid,
        tenant_id=obj.tenant_id,
        name=obj.name,
        slug=obj.slug,
        description=obj.description,
        is_system=obj.is_system,
        is_active=obj.is_active,
        created_at=obj.created_at,
        updated_at=obj.updated_at,
    )


class RoleRepositoryImpl(RoleRepository):

    @property
    def _model(self):
        from accounts.models.roles import Role
        return Role

    def save(self, entity: RoleEntity) -> RoleEntity:
        if entity.id:
            obj = self._model.all_objects.filter(pk=entity.id).first()
            if not obj:
                raise ValueError("Role not found to update")
            obj.name = entity.name.strip()
            obj.slug = entity.slug.strip().lower()
            obj.description = entity.description
            obj.is_active = entity.is_active
            obj.save()
        else:
            obj = self._model(
                uuid=entity.uuid,
                tenant_id=entity.tenant_id,
                name=entity.name.strip(),
                slug=entity.slug.strip().lower(),
                description=entity.description,
                is_system=entity.is_system,
                is_active=entity.is_active,
            )
            obj.save()

        return _model_to_entity(obj)

    def find_by_uuid(self, role_uuid: uuid.UUID) -> RoleEntity | None:
        obj = self._model.all_objects.filter(uuid=role_uuid).first()
        return _model_to_entity(obj) if obj else None

    def exists_by_slug(self, tenant_id: int, slug: str, exclude_id: int | None = None) -> bool:
        qs = self._model.all_objects.filter(tenant_id=tenant_id, slug=slug.strip().lower())
        if exclude_id:
            qs = qs.exclude(pk=exclude_id)
        return qs.exists()

    def delete(self, role_uuid: uuid.UUID) -> bool:
        obj = self._model.all_objects.filter(uuid=role_uuid).first()
        if not obj:
            return False
        obj.delete()  # soft delete via safedelete
        return True

    def hard_delete(self, role_uuid: uuid.UUID) -> bool:
        obj = self._model.all_objects.filter(uuid=role_uuid).first()
        if not obj:
            return False
        from safedelete.models import HARD_DELETE
        obj.delete(force_policy=HARD_DELETE)
        return True
