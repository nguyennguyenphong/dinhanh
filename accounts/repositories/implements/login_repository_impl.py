# Path: accounts/repositories/implement/django_user_repository.py

from typing import Optional
from accounts.models import UserAccount
from accounts.domain.entities.login_entity import LoginEntity
from accounts.repositories.interfaces.login_repository_interface import ILoginRepository


class LoginRepositoryImpl(ILoginRepository):
    """
    Implementation of IUserRepository interacting directly with Django ORM.
    Translates UserAccount ORM model instances into clean Domain Entities.
    """

    def get_by_email(self, email: str) -> Optional[LoginEntity]:
        try:
            user_model = UserAccount.objects.get(email=email)
            return LoginEntity(
                id=user_model.id,
                email=user_model.email,
                is_active=user_model.is_active,
                is_staff=user_model.is_staff,
                is_superuser=user_model.is_superuser
            )
        except UserAccount.DoesNotExist:
            return None