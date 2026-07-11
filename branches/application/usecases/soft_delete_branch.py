from branches.repositories.interfaces.branch_audit_log_repository_interface import (
    IBranchAuditLogRepository,
)
from branches.repositories.interfaces.branch_repository_interface import (
    IBranchRepository,
)


class SoftDeleteBranchUseCase:

    def __init__(
        self, repo: IBranchRepository, audit_repo: IBranchAuditLogRepository
    ) -> None:
        self._repo = repo
        self._audit_repo = audit_repo

    def execute(
        self,
        branch_id: int,
        *,
        actor_id: int | None = None,
        actor_username: str | None = None,
    ) -> None:
        existing = self._repo.get_by_id(branch_id)
        if not existing:
            raise ValueError(f"Branch with ID {branch_id} not found.")

        # Log deletion details
        old_values = {
            "code": existing.code,
            "name": existing.name,
            "tenant_id": existing.tenant_id,
        }

        self._audit_repo.create_log(
            tenant_id=existing.tenant_id,
            branch_id=existing.id,
            action="DELETE",
            actor_id=actor_id,
            actor_username=actor_username,
            old_values=old_values,
        )

        self._repo.delete(branch_id)
