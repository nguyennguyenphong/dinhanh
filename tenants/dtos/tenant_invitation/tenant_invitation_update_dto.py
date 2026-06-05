from dataclasses import dataclass

@dataclass(frozen=True)
class TenantInvitationStatusUpdateDTO:
    status: str