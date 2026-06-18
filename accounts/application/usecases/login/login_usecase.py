import logging

from accounts.application.dtos import LoginDTO
from accounts.repositories.interfaces.login_repository_interface import ILoginRepository
from accounts.services.login import LoginService
from accounts.policies.login_policy import LoginPolicy
from accounts.exceptions.exception import AuthenticationError, PermissionDeniedError
from accounts.domain.entities.login_entity import LoginEntity

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
        if not self._auth_service.verify_credentials(dto, request):
            raise AuthenticationError("Sai email hoặc mật khẩu")

        user_entity = self._repository.get_by_email(dto.email)
        if not user_entity:
            raise AuthenticationError("Account records matching credentials not found.")

        if not LoginPolicy.is_allowed_to_login(user_entity):
            raise PermissionDeniedError("Your account has been deactivated.")

        return user_entity