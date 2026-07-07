from dataclasses import dataclass


@dataclass(frozen=True)
class MenuItemRoleDeleteDto:
    id: int
    tenant_id: int
