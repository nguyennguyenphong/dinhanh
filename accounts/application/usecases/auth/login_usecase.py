import logging

from accounts.application.dtos import LoginDTO
from accounts.domain.entities.auth_user_entity import AuthUserEntity
from accounts.exceptions.exception import AuthenticationError, PermissionDeniedError
from accounts.policies.login_policy import LoginPolicy
from accounts.repositories.interfaces.auth_repository_interface import IAuthRepository
from accounts.services.auth.auth_service import LoginService

logger = logging.getLogger(__name__)


class LoginUseCase:
    """
    Coordinates data access, credential mapping, and policy validation
    to successfully authorize a user session.
    """

    def __init__(self, repository: IAuthRepository, auth_service: LoginService):
        self._repository = repository
        self._auth_service = auth_service

    def execute(self, dto: LoginDTO, request=None) -> AuthUserEntity:
        user_entity = self._repository.get_by_email(dto.email)
        if not user_entity:
            raise AuthenticationError("Tài khoản không tồn tại trên hệ thống.")

        if not LoginPolicy.is_allowed_to_login(user_entity):
            raise PermissionDeniedError(
                "Tài khoản chưa được xác minh OTP hoặc đã bị vô hiệu hóa."
            )

        user = self._auth_service.verify_credentials(dto, request)
        if not user:
            raise AuthenticationError("Mật khẩu không chính xác.")

        return user_entity
