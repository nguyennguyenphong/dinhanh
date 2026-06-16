from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class MenuGroupEntity:
    """
    Domain representation of a MenuGroup.
    Maintains business invariants and is completely decoupled from the persistence layer.
    """

    id: int | None
    uuid: uuid.UUID
    tenant_id: int
    code: str
    label: str
    icon: str | None
    sort_order: int
    is_active: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # Optional: For advanced DDD to track side-effects (e.g., clearing tenant menu cache)
    domain_events: list[Any] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        """
        Validates domain invariants right after entity initialization.
        Ensures the entity can never exist in an invalid state.
        """
        if not self.code or not self.code.strip():
            raise ValueError("MenuGroup code cannot be empty.")

        if not self.label or not self.label.strip():
            raise ValueError("MenuGroup label cannot be empty.")

        if self.tenant_id <= 0:
            raise ValueError("Invalid tenant_id. Must be a positive integer.")

    # ------------------------------------------------------------------
    # Business Rules / Behavior
    # ------------------------------------------------------------------

    def deactivate(self) -> None:
        """
        Deactivates the menu group, making it invisible to end-users.
        """
        if self.is_active:
            self.is_active = False
            # Example of production pattern: record a domain event if needed
            # self.domain_events.append(MenuGroupDeactivatedEvent(menu_group_id=self.id))

    def activate(self) -> None:
        """
        Activates the menu group, making it visible to end-users.
        """
        self.is_active = True

    def update_display(self, label: str, icon: str | None, sort_order: int) -> None:
        """
        Updates the presentation details of the menu group.
        """
        if not label or not label.strip():
            raise ValueError("Label cannot be empty.")

        self.label = label.strip()
        self.icon = icon.strip() if icon else None
        self.sort_order = sort_order

    def update_timestamp(self, now: datetime) -> None:
        """
        Updates the modification timestamp. Typically called by the repository layer before saving.
        """
        self.updated_at = now
