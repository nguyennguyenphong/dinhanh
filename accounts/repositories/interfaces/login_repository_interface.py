# Path: accounts/repositories/interfaces/user_repository_interface.py

from abc import ABC, abstractmethod
from typing import Optional

from accounts.domain.entities.login_entity import LoginEntity


class ILoginRepository(ABC):
    """
    Interface for UserAccount data access operations.
    Enforces inversion of control between business logic and database.
    """

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[LoginEntity]:
        """Retrieve a domain UserEntity by their unique email address."""
