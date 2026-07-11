from __future__ import annotations

from abc import ABC, abstractmethod


class IBranchAuditLogRepository(ABC):
    """Contract for Branch audit log persistence."""

    @abstractmethod
    def create_log(
        self,
        *,
        tenant_id: int,
        branch_id: int | None,
        action: str,
        actor_id: int | None = None,
        actor_username: str | None = None,
        old_values: dict | None = None,
        new_values: dict | None = None,
        reason: str | None = None,
    ) -> None:
        pass

    @abstractmethod
    def list_by_branch(
        self,
        branch_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict], int]:
        pass
