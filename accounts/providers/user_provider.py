from __future__ import annotations

from accounts.application.usecases.users.create_user_usecase import CreateUserUseCase
from accounts.application.usecases.users.hard_delete_user_usecase import (
    HardDeleteUserUseCase,
)
from accounts.application.usecases.users.soft_delete_user_usecase import (
    SoftDeleteUserUseCase,
)
from accounts.application.usecases.users.update_user_usecase import UpdateUserUseCase
from accounts.application.usecases.users.list_users_usecase import ListUsersUseCase
from accounts.repositories.implement.user_repository_impl import UserRepositoryImpl


class UserProvider:
    """
    Dependency Injection Container for User operations.
    """

    @staticmethod
    def create_user() -> CreateUserUseCase:
        repo = UserRepositoryImpl()
        return CreateUserUseCase(repository=repo)

    @staticmethod
    def update_user() -> UpdateUserUseCase:
        repo = UserRepositoryImpl()
        return UpdateUserUseCase(repository=repo)

    @staticmethod
    def soft_delete_user() -> SoftDeleteUserUseCase:
        repo = UserRepositoryImpl()
        return SoftDeleteUserUseCase(repository=repo)

    @staticmethod
    def hard_delete_user() -> HardDeleteUserUseCase:
        repo = UserRepositoryImpl()
        return HardDeleteUserUseCase(repository=repo)

    @staticmethod
    def list_users() -> ListUsersUseCase:
        repo = UserRepositoryImpl()
        return ListUsersUseCase(repository=repo)
