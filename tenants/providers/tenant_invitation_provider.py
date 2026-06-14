"""
Dependency injection provider for the Tenant bounded context.

Usage:
    from tenants.providers import TenantInvitationProvider

    use_case = TenantProvider.create_tenant_use_case()
    result = use_case.execute(dto, actor_id=request.user.pk, ...)
"""

from __future__ import annotations

from tenants.application.usecases import (
    AcceptInvitationUseCase,
    CreateInvitationUseCase,
    ListInvitationsUseCase,
)
from tenants.repositories.implement import TenantInvitationRepositoryImpl


class TenantInvitationProvider:
    """
    Static factory — instantiates concrete repos and injects them into use-cases.
    Swap any repository implementation here without touching business logic.
    """

    @staticmethod
    def _invitation_repo() -> TenantInvitationRepositoryImpl:
        return TenantInvitationRepositoryImpl()

    # ------------------------------------------------------------------ #
    # Use-case factories                                                   #
    # ------------------------------------------------------------------ #

    @classmethod
    def create_invitation(cls) -> CreateInvitationUseCase:
        return CreateInvitationUseCase(
            cls._tenant_repo(), cls._invitation_repo(), cls._audit_repo()
        )

    @classmethod
    def accept_invitation(cls) -> AcceptInvitationUseCase:
        return AcceptInvitationUseCase(cls._invitation_repo(), cls._audit_repo())

    @classmethod
    def list_invitations(cls) -> ListInvitationsUseCase:
        return ListInvitationsUseCase(cls._invitation_repo())

