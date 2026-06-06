from dataclasses import dataclass

@dataclass
class CreateTenantInvitationDTO:
    tenant_id: int
    email: str
    invited_by_id: int
    expires_in_days: int = 7
 