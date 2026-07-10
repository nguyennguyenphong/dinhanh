# Path: accounts/repositories/implement/django_user_repository.py

from typing import Optional

from accounts.domain.entities.auth_user_entity import AuthUserEntity
from accounts.models import UserAccount
from accounts.repositories.interfaces.auth_repository_interface import IAuthRepository


class AuthRepositoryImpl(IAuthRepository):
    """
    Implementation of IAuthRepository interacting directly with Django ORM.
    Translates UserAccount ORM model instances into clean Domain Entities.
    """

    def get_by_email(self, email: str) -> Optional[AuthUserEntity]:
        try:
            user_model = UserAccount.objects.get(email=email)
            return AuthUserEntity(
                id=user_model.id,
                email=user_model.email,
                is_active=user_model.is_active,
                is_staff=user_model.is_staff,
                is_superuser=user_model.is_superuser,
            )
        except UserAccount.DoesNotExist:
            return None
