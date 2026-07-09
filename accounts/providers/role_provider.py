from __future__ import annotations

from accounts.application.usecases.roles.create_role_usecase import CreateRoleUseCase
from accounts.application.usecases.roles.update_role_usecase import UpdateRoleUseCase
from accounts.application.usecases.roles.soft_delete_role_usecase import SoftDeleteRoleUseCase
from accounts.application.usecases.roles.hard_delete_role_usecase import HardDeleteRoleUseCase
from accounts.repositories.implements.role_repository_impl import RoleRepositoryImpl


class RoleProvider:
    """Dependency injection assembler for Role operations."""

    @staticmethod
    def create_role() -> CreateRoleUseCase:
        repo = RoleRepositoryImpl()
        return CreateRoleUseCase(repository=repo)

    @staticmethod
    def update_role() -> UpdateRoleUseCase:
        repo = RoleRepositoryImpl()
        return UpdateRoleUseCase(repository=repo)

    @staticmethod
    def soft_delete_role() -> SoftDeleteRoleUseCase:
        repo = RoleRepositoryImpl()
        return SoftDeleteRoleUseCase(repository=repo)

    @staticmethod
    def hard_delete_role() -> HardDeleteRoleUseCase:
        repo = RoleRepositoryImpl()
        return HardDeleteRoleUseCase(repository=repo)
