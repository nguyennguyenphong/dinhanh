from __future__ import annotations

import uuid
from typing import Any

from accounts.domain.entities.user_entity import UserEntity
from accounts.repositories.interfaces.user_repository_interface import UserRepository


def _model_to_entity(obj: Any) -> UserEntity:
    return UserEntity(
        id=obj.pk,
        uuid=obj.uuid,
        tenant_id=obj.tenant_id,
        username=obj.username,
        email=obj.email,
        full_name=obj.full_name,
        phone=obj.phone,
        avatar=obj.avatar,
        is_active=obj.is_active,
        hashed_password=obj.password,
        created_at=obj.created_at,
        updated_at=obj.updated_at,
    )


class UserRepositoryImpl(UserRepository):

    @property
    def _qs(self):
        from accounts.models import UserAccount

        return UserAccount.objects

    def save(self, entity: UserEntity) -> UserEntity:
        from accounts.models import UserAccount

        if entity.id:
            obj = self._qs.filter(pk=entity.id).first()
            if not obj:
                raise ValueError("User not found to update")
            obj.username = entity.username.strip().lower()
            obj.email = entity.email.strip().lower()
            obj.full_name = entity.full_name
            obj.phone = entity.phone
            obj.avatar = entity.avatar
            obj.is_active = entity.is_active
            obj.password = entity.hashed_password
            obj.save()
        else:
            obj = UserAccount(
                uuid=entity.uuid,
                tenant_id=entity.tenant_id,
                username=entity.username.strip().lower(),
                email=entity.email.strip().lower(),
                full_name=entity.full_name,
                phone=entity.phone,
                avatar=entity.avatar,
                is_active=entity.is_active,
                password=entity.hashed_password,
            )
            obj.save()

        return _model_to_entity(obj)

    def find_by_uuid(self, user_uuid: uuid.UUID) -> UserEntity | None:
        obj = self._qs.filter(uuid=user_uuid).first()
        return _model_to_entity(obj) if obj else None

    def exists_by_username(
        self, tenant_id: int, username: str, exclude_id: int | None = None
    ) -> bool:
        qs = self._qs.filter(tenant_id=tenant_id, username=username.strip().lower())
        if exclude_id:
            qs = qs.exclude(pk=exclude_id)
        return qs.exists()

    def exists_by_email(
        self, tenant_id: int, email: str, exclude_id: int | None = None
    ) -> bool:
        qs = self._qs.filter(tenant_id=tenant_id, email=email.strip().lower())
        if exclude_id:
            qs = qs.exclude(pk=exclude_id)
        return qs.exists()

    def delete(self, user_uuid: uuid.UUID) -> bool:
        obj = self._qs.filter(uuid=user_uuid).first()
        if not obj:
            return False
        obj.is_active = False
        obj.save()
        return True

    def hard_delete(self, user_uuid: uuid.UUID) -> bool:
        obj = self._qs.filter(uuid=user_uuid).first()
        if not obj:
            return False
        obj.delete()
        return True
