class AccountDomainError(Exception):
    """Base exception for all domain-specific errors in accounts app."""


class AuthenticationError(AccountDomainError):
    """Raised when authentication credentials (email/password) are invalid."""


class PermissionDeniedError(AccountDomainError):
    """Raised when the user is authenticated but violates access policies."""
