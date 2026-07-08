from __future__ import annotations

from branches.application.usecases.create_branch import CreateBranchUseCase
from branches.application.usecases.delete_branch import DeleteBranchUseCase
from branches.application.usecases.get_branch import GetBranchUseCase
from branches.application.usecases.list_branches import ListBranchesUseCase
from branches.application.usecases.update_branch import UpdateBranchUseCase
from branches.repositories.implement.branch_repository_impl import BranchRepositoryImpl


class BranchProvider:
    _repo = BranchRepositoryImpl()

    @classmethod
    def create_branch(cls) -> CreateBranchUseCase:
        return CreateBranchUseCase(cls._repo)

    @classmethod
    def update_branch(cls) -> UpdateBranchUseCase:
        return UpdateBranchUseCase(cls._repo)

    @classmethod
    def delete_branch(cls) -> DeleteBranchUseCase:
        return DeleteBranchUseCase(cls._repo)

    @classmethod
    def get_branch(cls) -> GetBranchUseCase:
        return GetBranchUseCase(cls._repo)

    @classmethod
    def list_branches(cls) -> ListBranchesUseCase:
        return ListBranchesUseCase(cls._repo)
