from dataclasses import dataclass


@dataclass(frozen=True)
class MenuItemDeleteDto:
    """Confirm the deletion request for a MenuItem."""

    id: int
    tenant_id: int
