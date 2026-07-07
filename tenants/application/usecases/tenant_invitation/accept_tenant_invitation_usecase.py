"""
Use-cases for TenantInvitation operations.
"""

from __future__ import annotations

from django.utils import timezone

from tenants.application.dtos.tenant_invitation.accept_tenant_invitation_dto import (
    AcceptTenantInvitationDTO,
)
from tenants.domain.entities.tenant_invitation_entity import TenantInvitationEntity
from tenants.exceptions.exception import (
    TenantInvitationAlreadyUsedError,
    TenantInvitationError,
    TenantInvitationExpiredError,
)
from tenants.repositories.interfaces.tenant_audit_log_repository_interface import (
    ITenantAuditLogRepository,
)
from tenants.repositories.interfaces.tenant_invitation_repository_interface import (
    ITenantInvitationRepository,
)


class AcceptInvitationUseCase:
    def __init__(
        self,
        invitation_repo: ITenantInvitationRepository,
        audit_repo: ITenantAuditLogRepository,
    ):
        self._invitation_repo = invitation_repo
        self._audit_repo = audit_repo

    def execute(
        self,
        dto: AcceptTenantInvitationDTO,
        *,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TenantInvitationEntity:
        invitation = self._invitation_repo.get_by_token(dto.token)
        if not invitation:
            raise TenantInvitationError(f"Thư mời với mã '{dto.token}' không tồn tại.")

        now = timezone.now()
        if invitation.status != "PENDING":
            raise TenantInvitationAlreadyUsedError(dto.token)
        if invitation.is_expired(now):
            self._invitation_repo.update_status(invitation.id, "EXPIRED")  # type: ignore[arg-type]
            raise TenantInvitationExpiredError(dto.token)

        saved = self._invitation_repo.update_status(
            invitation.id,  # type: ignore[arg-type]
            "ACCEPTED",
            accepted_at=now,
        )

        self._audit_repo.create_log(
            tenant_id=invitation.tenant_id,
            user_id=None,
            username=invitation.email,
            action="UPDATE",
            module="invitations",
            object_type="TenantInvitation",
            object_id=str(invitation.id),
            object_repr=f"Invitation accepted by {invitation.email}",
            old_values={"status": "PENDING"},
            new_values={"status": "ACCEPTED"},
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return saved
