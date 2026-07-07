from dataclasses import dataclass


@dataclass(frozen=True)
class MenuItemCreateDto:
    """Collect data from the MenuItem creation form."""

    tenant: int
    code: str
    label: str
    group_id: int | None = None
    parent_id: int | None = None
    url_name: str | None = None
    url_path: str | None = None
    icon: str | None = None
    badge: str | None = None
    permission_code: str | None = None
    sort_order: int = 0
    open_in_new_tab: bool = False
    is_active: bool = True
    is_hidden: bool = False
