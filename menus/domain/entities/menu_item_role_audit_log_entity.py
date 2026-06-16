from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from menus.contants import MenuItemRoleAuditAction


@dataclass
class MenuItemRoleAuditLogEntity:
    """
    Domain representation of a MenuItemRoleAuditLog.
    Maintains domain-level invariants and contains core business rules.
    """

    id: int | None
    tenant_id: int
    menu_item_id: int
    action: MenuItemRoleAuditAction | str
    role_id: int | None = None
    actor_id: int | None = None
    actor_username: str | None = None
    affected_count: int = 1
    reason: str | None = None
    created_at: datetime | None = None

    # Infrastructure for Domain Events (CQRS/DDD pattern)
    domain_events: list[Any] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        """
        Validates domain invariants right after entity initialization.
        Ensures the entity cannot be instantiated in an illegal state.
        """
        # 1. Base identity validation
        if self.tenant_id <= 0:
            raise ValueError("Invalid tenant_id. Must be a positive integer.")
        
        if self.menu_item_id <= 0:
            raise ValueError("Invalid menu_item_id. Must be a positive integer.")

        # 2. Enum parsing & validation
        if isinstance(self.action, str):
            try:
                self.action = MenuItemRoleAuditAction(self.action)
            except ValueError:
                raise ValueError(
                    f"Invalid action '{self.action}'. Must be one of {[e.value for e in MenuItemRoleAuditAction]}."
                )

        # 3. Business Invariant: Relationships validity
        if self.role_id is not None and self.role_id <= 0:
            raise ValueError("Invalid role_id. Must be a positive integer if provided.")
            
        if self.actor_id is not None and self.actor_id <= 0:
            raise ValueError("Invalid actor_id. Must be a positive integer if provided.")

        # 4. Business Invariant: Single vs Batch operation rules
        if self.action in [MenuItemRoleAuditAction.ASSIGN, MenuItemRoleAuditAction.REVOKE]:
            if self.role_id is None:
                raise ValueError(f"Action '{self.action.value}' requires a specific 'role_id'.")
            if self.affected_count != 1:
                raise ValueError(f"Single action '{self.action.value}' must have affected_count equal to 1.")

        if self.action in [MenuItemRoleAuditAction.BATCH_ASSIGN, MenuItemRoleAuditAction.BATCH_REVOKE]:
            if self.role_id is not None:
                raise ValueError(f"Batch action '{self.action.value}' should not reference a single 'role_id'.")
            if self.affected_count <= 0:
                raise ValueError(f"Batch action '{self.action.value}' must have affected_count greater than 0.")

        # 5. Clean text inputs
        if self.actor_username:
            self.actor_username = self.actor_username.strip()
        if self.reason:
            self.reason = self.reason.strip()

    # ------------------------------------------------------------------
    # Domain Factory Methods
    # ------------------------------------------------------------------

    @classmethod
    def log_single_action(
        cls,
        tenant_id: int,
        menu_item_id: int,
        role_id: int,
        action: MenuItemRoleAuditAction | str,
        actor_id: int | None = None,
        actor_username: str | None = None,
        reason: str | None = None,
    ) -> MenuItemRoleAuditLogEntity:
        """
        Named constructor explicitly for single role modification.
        """
        return cls(
            id=None,
            tenant_id=tenant_id,
            menu_item_id=menu_item_id,
            role_id=role_id,
            action=action,
            actor_id=actor_id,
            actor_username=actor_username,
            affected_count=1,
            reason=reason,
            created_at=None,
        )

    @classmethod
    def log_batch_action(
        cls,
        tenant_id: int,
        menu_item_id: int,
        action: MenuItemRoleAuditAction | str,
        affected_count: int,
        actor_id: int | None = None,
        actor_username: str | None = None,
        reason: str | None = None,
    ) -> MenuItemRoleAuditLogEntity:
        """
        Named constructor explicitly for batch roles modifications.
        """
        return cls(
            id=None,
            tenant_id=tenant_id,
            menu_item_id=menu_item_id,
            role_id=None,
            action=action,
            actor_id=actor_id,
            actor_username=actor_username,
            affected_count=affected_count,
            reason=reason,
            created_at=None,
        )

    # ------------------------------------------------------------------
    # Business Logic / Queries
    # ------------------------------------------------------------------

    def is_batch_operation(self) -> bool:
        """
        Check if the log entry belongs to a mass update.
        """
        return self.action in [MenuItemRoleAuditAction.BATCH_ASSIGN, MenuItemRoleAuditAction.BATCH_REVOKE]

    def is_assignment(self) -> bool:
        """
        Helper rule to check if permissions were granted.
        """
        return self.action in [MenuItemRoleAuditAction.ASSIGN, MenuItemRoleAuditAction.BATCH_ASSIGN]

    def requires_compliance_review(self) -> bool:
        """
        An example of production-level compliance rule: 
        Flag any batch revocation or non-reason changes for specific audits.
        """
        if self.is_batch_operation() and self.affected_count > 10:
            return True
        if self.is_assignment() and not self.reason:
            return True
        return False