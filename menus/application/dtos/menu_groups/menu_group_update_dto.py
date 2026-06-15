from dataclasses import dataclass

import uuid


@dataclass(frozen=True)
class MenuGroupUpdateDto:
    """Collect data from the MenuGroup editing form (using uuid or id as the identifier)."""
    id: int
    uuid: uuid.UUID
    code: str
    label: str
    sort_order: int
    icon: str | None = None
    is_active: bool = True