from accounts.application.usecases.auth import (
    LoginUseCase,
    RegisterUseCase,
    VerifyEmailUseCase,
    ForgotPasswordUseCase,
    ConfirmPasswordResetUseCase,
)
from accounts.repositories.implement.auth_repository_impl import AuthRepositoryImpl
from accounts.repositories.implement.user_repository_impl import UserRepositoryImpl
from accounts.repositories.implement.otp_code_repository_impl import OTPCodeRepositoryImpl
from accounts.services.auth.auth_service import LoginService


class AuthProvider:
    """
    Dependency Injection Container / Service Registry.
    Assembles technological layers together before passing to Controllers/Views.
    """

    @staticmethod
    def authenticate_user() -> LoginUseCase:
        repo = AuthRepositoryImpl()
        auth_service = LoginService()
        return LoginUseCase(repository=repo, auth_service=auth_service)

    @staticmethod
    def register_user() -> RegisterUseCase:
        user_repo = UserRepositoryImpl()
        otp_repo = OTPCodeRepositoryImpl()
        return RegisterUseCase(user_repo=user_repo, otp_repo=otp_repo)

    @staticmethod
    def verify_email() -> VerifyEmailUseCase:
        user_repo = UserRepositoryImpl()
        otp_repo = OTPCodeRepositoryImpl()
        return VerifyEmailUseCase(user_repo=user_repo, otp_repo=otp_repo)

    @staticmethod
    def forgot_password() -> ForgotPasswordUseCase:
        user_repo = UserRepositoryImpl()
        otp_repo = OTPCodeRepositoryImpl()
        return ForgotPasswordUseCase(user_repo=user_repo, otp_repo=otp_repo)

    @staticmethod
    def confirm_password_reset() -> ConfirmPasswordResetUseCase:
        user_repo = UserRepositoryImpl()
        otp_repo = OTPCodeRepositoryImpl()
        return ConfirmPasswordResetUseCase(user_repo=user_repo, otp_repo=otp_repo)
