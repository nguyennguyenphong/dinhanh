class AccountDomainError(Exception):
    """Base exception for all domain-specific errors in accounts app."""
    pass


class AuthenticationError(AccountDomainError):
    """Raised when authentication credentials (email/password) are invalid."""
    pass


class PermissionDeniedError(AccountDomainError):
    """Raised when the user is authenticated but violates access policies."""
    pass