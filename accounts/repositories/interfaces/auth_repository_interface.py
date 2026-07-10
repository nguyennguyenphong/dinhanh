# Path: accounts/repositories/interfaces/user_repository_interface.py

from abc import ABC, abstractmethod
from typing import Optional

from accounts.domain.entities.auth_user_entity import AuthUserEntity


class IAuthRepository(ABC):
    """
    Interface for UserAccount data access operations.
    Enforces inversion of control between business logic and database.
    """

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[AuthUserEntity]:
        """Retrieve a domain AuthUserEntity by their unique email address."""
