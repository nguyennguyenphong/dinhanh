from __future__ import annotations

from accounts.application.usecases.permissions.create_permission_usecase import CreatePermissionUseCase
from accounts.application.usecases.permissions.update_permission_usecase import UpdatePermissionUseCase
from accounts.application.usecases.permissions.soft_delete_permission_usecase import SoftDeletePermissionUseCase
from accounts.application.usecases.permissions.hard_delete_permission_usecase import HardDeletePermissionUseCase
from accounts.repositories.implements.permission_repository_impl import PermissionRepositoryImpl


class PermissionProvider:
    """Dependency injection assembler for Permission operations."""

    @staticmethod
    def create_permission() -> CreatePermissionUseCase:
        repo = PermissionRepositoryImpl()
        return CreatePermissionUseCase(repository=repo)

    @staticmethod
    def update_permission() -> UpdatePermissionUseCase:
        repo = PermissionRepositoryImpl()
        return UpdatePermissionUseCase(repository=repo)

    @staticmethod
    def soft_delete_permission() -> SoftDeletePermissionUseCase:
        repo = PermissionRepositoryImpl()
        return SoftDeletePermissionUseCase(repository=repo)

    @staticmethod
    def hard_delete_permission() -> HardDeletePermissionUseCase:
        repo = PermissionRepositoryImpl()
        return HardDeletePermissionUseCase(repository=repo)
