from dataclasses import dataclass

@dataclass(frozen=True)
class MenuGroupSoftDeleteDto:
    """Confirm the temporary deletion request (Move to trash)."""
    id: int
    tenant_id: int