"""
Use-cases for TenantInvitation operations.
"""

from __future__ import annotations

from tenants.domain.entities.tenant_invitation_entity import TenantInvitationEntity
from tenants.repositories.interfaces.tenant_invitation_repository_interface import (
    ITenantInvitationRepository,
)


class ListInvitationsUseCase:
    def __init__(self, invitation_repo: ITenantInvitationRepository):
        self._invitation_repo = invitation_repo

    def execute(
        self,
        tenant_id: int,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[TenantInvitationEntity], int]:
        return self._invitation_repo.list_by_tenant(
            tenant_id, status=status, limit=limit, offset=offset
        )
