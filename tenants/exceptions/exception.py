"""
Domain-level exceptions for the Tenant bounded context.
These are raised by domain/service layer and translated to HTTP responses in views.
"""


class TenantDomainError(Exception):
    """Base class for all tenant domain errors."""


class TenantNotFoundError(TenantDomainError):
    def __init__(self, identifier: str | int):
        super().__init__(f"Tenant not found: {identifier}")
        self.identifier = identifier


class TenantAlreadyExistsError(TenantDomainError):
    def __init__(self, code: str):
        super().__init__(f"Tenant with code '{code}' already exists.")
        self.code = code


class TenantInactiveError(TenantDomainError):
    def __init__(self, code: str):
        super().__init__(f"Tenant '{code}' is inactive.")
        self.code = code


class TenantSubscriptionExpiredError(TenantDomainError):
    def __init__(self, code: str):
        super().__init__(f"Tenant '{code}' subscription has expired.")
        self.code = code


class TenantLimitExceededError(TenantDomainError):
    def __init__(self, resource: str, limit: int):
        super().__init__(f"Tenant limit exceeded for '{resource}': max={limit}.")
        self.resource = resource
        self.limit = limit


class TenantFeatureFlagNotFoundError(TenantDomainError):
    def __init__(self, code: str):
        super().__init__(f"Feature flag '{code}' not found.")
        self.code = code


class TenantInvitationError(TenantDomainError):
    """Generic invitation error."""


class TenantInvitationExpiredError(TenantInvitationError):
    def __init__(self, token: str):
        super().__init__(f"Invitation token '{token}' has expired.")
        self.token = token


class TenantInvitationAlreadyUsedError(TenantInvitationError):
    def __init__(self, token: str):
        super().__init__(f"Invitation token '{token}' has already been used.")
        self.token = token