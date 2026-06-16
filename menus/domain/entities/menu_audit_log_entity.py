from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict

from menus.contants import MenuAuditAction


@dataclass
class MenuAuditLogEntity:
    """
    Domain representation of a MenuAuditLog.
    Maintains business invariants and is completely decoupled from the persistence layer.
    """

    id: int | None
    tenant_id: int
    action: MenuAuditAction | str
    old_values: Dict[str, Any] | None
    new_values: Dict[str, Any] | None
    actor_id: int | None = None
    created_at: datetime | None = None

    # Optional: For advanced DDD to track side-effects
    domain_events: list[Any] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        """
        Validates domain invariants right after entity initialization.
        Ensures the entity can never exist in an invalid state.
        """
        if self.tenant_id <= 0:
            raise ValueError("Invalid tenant_id. Must be a positive integer.")

        # Validate action against the MenuAuditAction Enum
        if isinstance(self.action, str):
            try:
                self.action = MenuAuditAction(self.action)
            except ValueError:
                raise ValueError(
                    f"Invalid action '{self.action}'. Must be one of {[e.value for e in MenuAuditAction]}."
                )

        # Invariant check for actor if provided
        if self.actor_id is not None and self.actor_id <= 0:
            raise ValueError(
                "Invalid actor_id. Must be a positive integer if provided."
            )

        # Business Rule: An audit log must have at least old_values or new_values
        # (Except for REORDER which might just log structural changes in values)
        if (
            self.action in [MenuAuditAction.CREATE, MenuAuditAction.UPDATE]
            and not self.new_values
        ):
            raise ValueError(f"Action '{self.action.value}' requires 'new_values'.")

    # ------------------------------------------------------------------
    # Factory Methods (Optional but highly recommended for Production)
    # ------------------------------------------------------------------

    @classmethod
    def create_log(
        cls,
        tenant_id: int,
        action: MenuAuditAction | str,
        old_values: Dict[str, Any] | None = None,
        new_values: Dict[str, Any] | None = None,
        actor_id: int | None = None,
    ) -> MenuAuditLogEntity:
        """
        Factory method to instantiate a new Audit Log from the domain/use-case layer.
        """
        return cls(
            id=None,
            tenant_id=tenant_id,
            action=action,
            old_values=old_values,
            new_values=new_values,
            actor_id=actor_id,
            created_at=None,  # Will be set by persistence layer (auto_now_add)
        )

    # ------------------------------------------------------------------
    # Business Rules / Behavior
    # ------------------------------------------------------------------

    def is_structural_change(self) -> bool:
        """
        Business rule to check if the log represents a structural reordering.
        """
        return self.action == MenuAuditAction.REORDER

    def get_changed_fields(self) -> list[str]:
        """
        Compares old_values and new_values to return a list of modified fields.
        Useful for presentation layers.
        """
        if not self.old_values or not self.new_values:
            return []

        changed = []
        for key, val in self.new_values.items():
            if self.old_values.get(key) != val:
                changed.append(key)
        return changed
