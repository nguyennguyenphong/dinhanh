from dataclasses import dataclass


@dataclass(frozen=True)
class LoginDTO:
    """
    Immutable input payload containing strict authentication credentials.
    """
    email: str
    password: str