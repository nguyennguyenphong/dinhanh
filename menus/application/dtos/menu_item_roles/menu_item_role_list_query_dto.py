from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class MenuItemRoleListQueryDto:
    tenant_id: int
    menu_item_id: Optional[int] = None
    role_id: Optional[int] = None
    limit: int = 50
    offset: int = 0
