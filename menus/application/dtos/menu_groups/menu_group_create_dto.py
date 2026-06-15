from dataclasses import dataclass


@dataclass(frozen=True)
class MenuGroupCreateDto:
    """Collect data from the MenuGroup creation form."""
    tenant: int
    code: str
    label: str
    sort_order: int
    icon: str | None = None
    is_active: bool = True