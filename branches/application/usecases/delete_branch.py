from __future__ import annotations

from branches.repositories.interfaces.branch_repository_interface import IBranchRepository


class DeleteBranchUseCase:

    def __init__(self, repo: IBranchRepository) -> None:
        self._repo = repo

    def execute(self, branch_id: int) -> None:
        existing = self._repo.get_by_id(branch_id)
        if not existing:
            raise ValueError(f"Branch with ID {branch_id} not found.")
        self._repo.delete(branch_id)
