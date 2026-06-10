"""
Abstract repository interfaces for the Tenant Invitation bounded context.
Concrete implementations live in repositories/implement/.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from tenants.domain.entities.tenant_invitation_entity import TenantInvitationEntity


class ITenantInvitationRepository(ABC):
    """Contract for invitation persistence."""

    @abstractmethod
    def get_by_token(self, token: str) -> TenantInvitationEntity | None: ...

    @abstractmethod
    def get_pending_by_email(
        self, tenant_id: int, email: str
    ) -> TenantInvitationEntity | None: ...

    @abstractmethod
    def list_by_tenant(
        self,
        tenant_id: int,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[TenantInvitationEntity], int]: ...

    @abstractmethod
    def create(self, entity: TenantInvitationEntity) -> TenantInvitationEntity: ...

    @abstractmethod
    def update_status(
        self,
        invitation_id: int,
        status: str,
        accepted_at: Any = None,
    ) -> TenantInvitationEntity: ...
