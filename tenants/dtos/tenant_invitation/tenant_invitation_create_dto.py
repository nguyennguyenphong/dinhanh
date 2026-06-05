from dataclasses import dataclass

@dataclass(frozen=True)
class TenantInvitationCreateDTO:
    email: str
    tenant_id: int
    invited_by_id: int
    expires_in_days: int = 7