from accounts.repositories.interfaces.auth_repository_interface import IAuthRepository
from accounts.repositories.interfaces.otp_code_repository_interface import (
    OTPCodeRepository,
)
from accounts.repositories.interfaces.permission_repository_interface import (
    PermissionRepository,
)
from accounts.repositories.interfaces.role_repository_interface import RoleRepository
from accounts.repositories.interfaces.user_repository_interface import UserRepository

__all__ = [
    "IAuthRepository",
    "OTPCodeRepository",
    "UserRepository",
    "RoleRepository",
    "PermissionRepository",
]
