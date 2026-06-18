from accounts.domain.entities.login_entity import LoginEntity


class LoginPolicy:
    """
    Encapsulates specific business rules regarding system entry and access control.
    """

    @staticmethod
    def is_allowed_to_login(user: LoginEntity) -> bool:
        """Verifies if the account is active in the system."""
        return user.is_active

    @staticmethod
    def is_administrative_user(user: LoginEntity) -> bool:
        """Determines if the account possesses staff or superuser management rights."""
        return user.is_active and (user.is_staff or user.is_superuser)

    @staticmethod
    def is_standard_client(user: LoginEntity) -> bool:
        """Determines if the account is a standard consumer/client."""
        return user.is_active and not user.is_staff and not user.is_superuser
