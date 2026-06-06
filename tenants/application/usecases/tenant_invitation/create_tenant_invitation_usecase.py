"""
Use-cases for TenantInvitation operations.
"""
from __future__ import annotations

import secrets
from datetime import timedelta

from django.utils import timezone

from tenants.application.dtos.tenant_invitation.create_tenant_invitation_dto import CreateTenantInvitationDTO
from tenants.domain.entities.tenant_invitation_entity import TenantInvitationEntity
from tenants.exceptions.exception import TenantNotFoundError
from tenants.repositories.interfaces.tenant_audit_log_repository_interface import ITenantAuditLogRepository
from tenants.repositories.interfaces.tenant_invitation_repository_interface import ITenantInvitationRepository
from tenants.repositories.interfaces.tenant_repository_interface import ITenantRepository



class CreateInvitationUseCase:
    def __init__(
        self,
        tenant_repo: ITenantRepository,
        invitation_repo: ITenantInvitationRepository,
        audit_repo: ITenantAuditLogRepository,
    ):
        self._tenant_repo = tenant_repo
        self._invitation_repo = invitation_repo
        self._audit_repo = audit_repo

    def execute(
        self,
        dto: CreateTenantInvitationDTO,
        *,
        actor_username: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TenantInvitationEntity:
        tenant = self._tenant_repo.get_by_id(dto.tenant_id)
        if not tenant:
            raise TenantNotFoundError(dto.tenant_id)

        # Invalidate existing pending invitation for same email
        existing = self._invitation_repo.get_pending_by_email(
            dto.tenant_id, dto.email
        )
        if existing:
            self._invitation_repo.update_status(existing.id, "EXPIRED")  # type: ignore[arg-type]

        now = timezone.now()
        entity = TenantInvitationEntity(
            id=None,
            tenant_id=dto.tenant_id,
            email=dto.email.lower().strip(),
            token=secrets.token_urlsafe(48),
            status="PENDING",
            invited_by_id=dto.invited_by_id,
            expires_at=now + timedelta(days=dto.expires_in_days),
        )
        saved = self._invitation_repo.create(entity)

        self._audit_repo.create_log(
            tenant_id=dto.tenant_id,
            user_id=dto.invited_by_id,
            username=actor_username,
            action="CREATE",
            module="invitations",
            object_type="TenantInvitation",
            object_id=str(saved.id),
            object_repr=f"Invitation to {saved.email}",
            new_values={"email": saved.email, "expires_at": saved.expires_at.isoformat()},
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return saved
