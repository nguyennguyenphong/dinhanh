from typing import Any


class MenuItemDomainError(Exception):
    """Base class for all MenuItem domain errors."""


class MenuItemNotFoundError(MenuItemDomainError):
    """Raised when a specific MenuItem cannot be found by its identifier."""

    def __init__(self, identifier: Any):
        super().__init__(f"MenuItem with identifier '{identifier}' not found.")


class MenuItemAlreadyExistsError(MenuItemDomainError):
    """Raised when a duplicate unique code is detected within a tenant scope."""

    def __init__(self, tenant_id: int, code: str):
        super().__init__(
            f"MenuItem code '{code}' already exists for tenant {tenant_id}."
        )
