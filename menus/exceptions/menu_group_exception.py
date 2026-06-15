from typing import Any


class MenuGroupNotFoundError(Exception):
    """Raised when a specific MenuGroup cannot be found by its identifier."""
    def __init__(self, identifier: Any):
        super().__init__(f"MenuGroup with identifier '{identifier}' not found.")


class MenuGroupAlreadyExistsError(Exception):
    """Raised when a duplicate unique code is detected within a tenant scope."""
    def __init__(self, tenant_id: int, code: str):
        super().__init__(f"MenuGroup code '{code}' already exists for tenant {tenant_id}.")