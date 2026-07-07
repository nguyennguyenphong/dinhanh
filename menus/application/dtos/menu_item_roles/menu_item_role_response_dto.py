from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from menus.domain.entities.menu_item_role_entity import MenuItemRoleEntity


@dataclass(frozen=True)
class MenuItemRoleResponseDto:
    id: int
    uuid: str
    menu_item_id: int
    role_id: int
    tenant_id: int

    @classmethod
    def from_entity(cls, entity: MenuItemRoleEntity) -> MenuItemRoleResponseDto:
        return cls(
            id=entity.id,
            uuid=entity.uuid or "",
            menu_item_id=entity.menu_item_id,
            role_id=entity.role_id,
            tenant_id=entity.tenant_id,
        )
