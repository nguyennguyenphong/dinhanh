from __future__ import annotations

from branches.models.branch_audit_log import BranchAuditLog
from branches.repositories.interfaces.branch_audit_log_repository_interface import (
    IBranchAuditLogRepository,
)


class BranchAuditLogRepositoryImpl(IBranchAuditLogRepository):

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
        BranchAuditLog.objects.create(
            tenant_id=tenant_id,
            branch_id=branch_id,
            action=action,
            actor_id=actor_id,
            actor_username=actor_username,
            old_values=old_values,
            new_values=new_values,
            reason=reason,
        )

    def list_by_branch(
        self,
        branch_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict], int]:
        qs = BranchAuditLog.objects.filter(branch_id=branch_id)
        total = qs.count()
        records = list(
            qs.values(
                "id",
                "tenant_id",
                "branch_id",
                "action",
                "actor_id",
                "actor_username",
                "old_values",
                "new_values",
                "reason",
                "created_at",
            )[offset : offset + limit]
        )
        return records, total
