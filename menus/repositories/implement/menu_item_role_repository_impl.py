from __future__ import annotations

from typing import List, Optional

from menus.domain.entities.menu_item_role_entity import MenuItemRoleEntity
from menus.models.menu_item_roles import MenuItemRole
from menus.repositories.interfaces.menu_item_role_repository_interface import (
    IMenuItemRoleRepository,
)


def _model_to_entity(model: MenuItemRole) -> MenuItemRoleEntity:
    return MenuItemRoleEntity(
        id=model.id,
        uuid=str(model.uuid),
        menu_item_id=model.menu_item_id,
        role_id=model.role_id,
        tenant_id=model.menu_item.tenant_id,
    )


class MenuItemRoleRepositoryImpl(IMenuItemRoleRepository):
    """Django ORM implementation of IMenuItemRoleRepository."""

    def __init__(self):
        self._qs = MenuItemRole.objects.all().select_related("menu_item", "role")

    def get_by_id(self, pk: int) -> Optional[MenuItemRoleEntity]:
        obj = self._qs.filter(pk=pk).first()
        return _model_to_entity(obj) if obj else None

    def get_by_uuid(self, pk_uuid: str) -> Optional[MenuItemRoleEntity]:
        obj = self._qs.filter(uuid=pk_uuid).first()
        return _model_to_entity(obj) if obj else None

    def create(self, **kwargs) -> MenuItemRoleEntity:
        obj = MenuItemRole(**kwargs)
        obj.save()
        return _model_to_entity(obj)

    def delete(self, entity: MenuItemRoleEntity) -> None:
        obj = MenuItemRole.objects.filter(pk=entity.id).first()
        if obj:
            obj.delete()

    def hard_delete(self, entity: MenuItemRoleEntity) -> None:
        obj = MenuItemRole.objects.filter(pk=entity.id).first()
        if obj:
            obj.delete(force_policy=True)

    def list(
        self,
        *,
        tenant_id: int,
        menu_item_id: Optional[int] = None,
        role_id: Optional[int] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[List[MenuItemRoleEntity], int]:
        qs = self._qs.filter(menu_item__tenant_id=tenant_id)
        if menu_item_id is not None:
            qs = qs.filter(menu_item_id=menu_item_id)
        if role_id is not None:
            qs = qs.filter(role_id=role_id)

        total = qs.count()
        items = [_model_to_entity(obj) for obj in qs[offset : offset + limit]]
        return items, total

    def exists(self, menu_item_id: int, role_id: int) -> bool:
        return MenuItemRole.objects.filter(
            menu_item_id=menu_item_id, role_id=role_id
        ).exists()
