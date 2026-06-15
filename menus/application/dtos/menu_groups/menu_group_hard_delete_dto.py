from dataclasses import dataclass


@dataclass(frozen=True)
class MenuGroupHardDeleteDto:
    """Confirm the request to permanently delete from the database (Caution required)."""
    id: int
    tenant_id: int