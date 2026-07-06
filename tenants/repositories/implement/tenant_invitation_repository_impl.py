"""
Django ORM concrete implementations for:
  - TenantInvitation
"""

from __future__ import annotations

from typing import Any

from tenants.domain.entities.tenant_invitation_entity import TenantInvitationEntity
from tenants.repositories.interfaces.tenant_invitation_repository_interface import (
    ITenantInvitationRepository,
)


def _inv_model_to_entity(obj: Any) -> TenantInvitationEntity:
    return TenantInvitationEntity(
        id=obj.pk,
        tenant_id=obj.tenant_id,
        email=obj.email,
        token=obj.token,
        status=obj.status,
        invited_by_id=obj.invited_by_id,
        expires_at=obj.expires_at,
        accepted_at=obj.accepted_at,
        created_at=obj.created_at,
    )


class TenantInvitationRepositoryImpl(ITenantInvitationRepository):

    def get_by_token(self, token: str) -> TenantInvitationEntity | None:
        from tenants.models.tenent_invitation import TenantInvitation

        obj = (
            TenantInvitation.objects.filter(token=token)
            .select_related("tenant")
            .first()
        )
        return _inv_model_to_entity(obj) if obj else None

    def get_pending_by_email(
        self, tenant_id: int, email: str
    ) -> TenantInvitationEntity | None:
        from tenants.models.tenent_invitation import TenantInvitation

        obj = TenantInvitation.objects.filter(
            tenant_id=tenant_id, email=email, status="PENDING"
        ).first()
        return _inv_model_to_entity(obj) if obj else None

    def list_by_tenant(
        self,
        tenant_id: int,
        status: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[TenantInvitationEntity], int]:
        from tenants.models.tenent_invitation import TenantInvitation

        qs = TenantInvitation.objects.filter(tenant_id=tenant_id)
        if status:
            qs = qs.filter(status=status)

        total = qs.count()
        items = [_inv_model_to_entity(obj) for obj in qs[offset : offset + limit]]
        return items, total

    def create(self, entity: TenantInvitationEntity) -> TenantInvitationEntity:
        from tenants.models.tenent_invitation import TenantInvitation

        obj = TenantInvitation.objects.create(
            tenant_id=entity.tenant_id,
            email=entity.email,
            token=entity.token,
            status=entity.status,
            invited_by_id=entity.invited_by_id,
            expires_at=entity.expires_at,
        )
        return _inv_model_to_entity(obj)

    def update_status(
        self,
        invitation_id: int,
        status: str,
        accepted_at: Any = None,
    ) -> TenantInvitationEntity:
        from tenants.models.tenent_invitation import TenantInvitation

        update_fields: dict[str, Any] = {"status": status}
        if accepted_at is not None:
            update_fields["accepted_at"] = accepted_at

        TenantInvitation.objects.filter(pk=invitation_id).update(**update_fields)
        obj = TenantInvitation.objects.get(pk=invitation_id)
        return _inv_model_to_entity(obj)
