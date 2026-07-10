from dataclasses import dataclass


@dataclass(frozen=True)
class AuthUserEntity:
    """
    Domain Entity representing the UserAccount.
    Pure Python object decoupled from Django's infrastructure.
    """

    id: int
    email: str
    is_active: bool
    is_staff: bool
    is_superuser: bool
