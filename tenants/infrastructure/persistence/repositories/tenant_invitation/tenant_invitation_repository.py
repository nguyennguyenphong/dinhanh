from typing import Optional

from tenants.models.tenent_invitation import TenantInvitation


class TenantInvitationRepository:

    @staticmethod
    def get_by_token(token: str) -> Optional[TenantInvitation]:
        return TenantInvitation.objects.filter(token=token).select_related('tenant').first()

    @staticmethod
    def create(data: dict) -> TenantInvitation:
        return TenantInvitation.objects.create(**data)

    @staticmethod
    def update_status(invitation: TenantInvitation, status: str) -> TenantInvitation:
        invitation.status = status
        invitation.save(update_fields=['status'])
        return invitation