import logging

from accounts.application.dtos import LoginDTO
from accounts.domain.entities.login_entity import LoginEntity
from accounts.exceptions.exception import AuthenticationError, PermissionDeniedError
from accounts.policies.login_policy import LoginPolicy
from accounts.repositories.interfaces.login_repository_interface import ILoginRepository
from accounts.services.login import LoginService

logger = logging.getLogger(__name__)


class LoginUseCase:
    """
    Coordinates data access, credential mapping, and policy validation
    to successfully authorize a user session.
    """

    def __init__(self, repository: ILoginRepository, auth_service: LoginService):
        self._repository = repository
        self._auth_service = auth_service

    def execute(self, dto: LoginDTO, request=None) -> LoginEntity:
        user = self._auth_service.verify_credentials(dto, request)

        if not user:
            raise AuthenticationError("Sai email hoặc mật khẩu.")

        user_entity = self._repository.get_by_email(dto.email)
        if not user_entity:
            raise AuthenticationError("Email hoặc mật khẩu không đúng")

        if not LoginPolicy.is_allowed_to_login(user_entity):
            raise PermissionDeniedError("Tài khoản đã bị vô hiệu hóa")

        return user_entity
