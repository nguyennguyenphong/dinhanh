from accounts.application.usecases.login import LoginUseCase
from accounts.repositories.implements.login_repository_impl import LoginRepositoryImpl
from accounts.services.login import LoginService


class LoginProvider:
    """
    Dependency Injection Container / Service Registry.
    Assembles technological layers together before passing to Controllers/Views.
    """

    @staticmethod
    def authenticate_user() -> LoginUseCase:
        repo = LoginRepositoryImpl()
        auth_service = LoginService()
        return LoginUseCase(repository=repo, auth_service=auth_service)
