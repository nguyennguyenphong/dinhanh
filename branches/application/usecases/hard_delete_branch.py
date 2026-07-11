from branches.repositories.interfaces.branch_audit_log_repository_interface import (
    IBranchAuditLogRepository,
)
from branches.repositories.interfaces.branch_repository_interface import (
    IBranchRepository,
)


class HardDeleteBranchUseCase:

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
        # We might need to look up the branch via all_objects / or standard since it might be soft-deleted already
        # Wait, if we want to hard delete an existing branch or soft-deleted one:
        # Let's fetch using Branch.all_objects in the repo.
        # But wait! Repo's get_by_id currently uses Branch.objects.get.
        # Let's make sure we log if it exists.
        # Let's check:
        from branches.models import Branch

        existing_model = Branch.all_objects.filter(id=branch_id).first()
        if not existing_model:
            raise ValueError(f"Branch with ID {branch_id} not found.")

        old_values = {
            "code": existing_model.code,
            "name": existing_model.name,
            "tenant_id": existing_model.tenant_id,
            "hard_deleted": True,
        }

        self._audit_repo.create_log(
            tenant_id=existing_model.tenant_id,
            branch_id=existing_model.id,
            action="DELETE",
            actor_id=actor_id,
            actor_username=actor_username,
            old_values=old_values,
            reason="Hard delete",
        )

        self._repo.hard_delete(branch_id)
