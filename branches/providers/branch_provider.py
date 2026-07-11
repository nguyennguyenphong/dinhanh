from __future__ import annotations

from branches.application.usecases.create_branch import CreateBranchUseCase
from branches.application.usecases.get_branch import GetBranchUseCase
from branches.application.usecases.hard_delete_branch import HardDeleteBranchUseCase
from branches.application.usecases.list_branches import ListBranchesUseCase
from branches.application.usecases.soft_delete_branch import SoftDeleteBranchUseCase
from branches.application.usecases.update_branch import UpdateBranchUseCase
from branches.providers.branch_audit_log_provider import BranchAuditLogProvider
from branches.repositories.implement.branch_repository_impl import BranchRepositoryImpl


class BranchProvider:
    _repo = BranchRepositoryImpl()

    @classmethod
    def _audit_repo(cls):
        return BranchAuditLogProvider._audit_repo()

    @classmethod
    def create_branch(cls) -> CreateBranchUseCase:
        return CreateBranchUseCase(cls._repo, cls._audit_repo())

    @classmethod
    def update_branch(cls) -> UpdateBranchUseCase:
        return UpdateBranchUseCase(cls._repo, cls._audit_repo())

    @classmethod
    def soft_delete_branch(cls) -> SoftDeleteBranchUseCase:
        return SoftDeleteBranchUseCase(cls._repo, cls._audit_repo())

    @classmethod
    def hard_delete_branch(cls) -> HardDeleteBranchUseCase:
        return HardDeleteBranchUseCase(cls._repo, cls._audit_repo())

    @classmethod
    def get_branch(cls) -> GetBranchUseCase:
        return GetBranchUseCase(cls._repo)

    @classmethod
    def list_branches(cls) -> ListBranchesUseCase:
        return ListBranchesUseCase(cls._repo)
