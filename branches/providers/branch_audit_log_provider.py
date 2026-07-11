from __future__ import annotations

from branches.repositories.implement.branch_audit_log_repository_impl import (
    BranchAuditLogRepositoryImpl,
)


class BranchAuditLogProvider:

    @staticmethod
    def _audit_repo() -> BranchAuditLogRepositoryImpl:
        return BranchAuditLogRepositoryImpl()
