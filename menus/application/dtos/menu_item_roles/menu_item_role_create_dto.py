from dataclasses import dataclass


@dataclass(frozen=True)
class MenuItemRoleCreateDto:
    menu_item_id: int
    role_id: int
