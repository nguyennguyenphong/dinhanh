"""
Django ORM concrete implementation of ITenantRepository.
All DB queries live here; the rest of the app never touches ORM directly.
"""

from __future__ import annotations

import uuid
from typing import Any

from django.db.models import Q

from tenants.domain.entities.tenant_entity import TenantEntity
from tenants.repositories.interfaces.tenant_repository_interface import (
    ITenantRepository,
)


def _model_to_entity(obj: Any) -> TenantEntity:
    """Convert a Tenant ORM instance to a domain TenantEntity."""
    return TenantEntity(
        id=obj.pk,
        uuid=obj.uuid,
        code=obj.code,
        name=obj.name,
        plan=obj.plan,
        is_active=obj.is_active,
        currency=obj.currency,
        exchange_rate=obj.exchange_rate,
        default_language=obj.default_language,
        timezone=obj.timezone,
        primary_color=obj.primary_color,
        max_users=obj.max_users,
        max_branches=obj.max_branches,
        max_vehicles=obj.max_vehicles,
        subscription_started_at=obj.subscription_started_at,
        subscription_expires_at=obj.subscription_expires_at,
        settings=obj.settings or {},
        domain=obj.domain,
        logo_url=obj.logo_url,
        created_at=obj.created_at,
        updated_at=obj.updated_at,
    )


class TenantRepositoryImpl(ITenantRepository):

    @property
    def _qs(self):
        # Lazy import to avoid circular imports at module load time
        from tenants.models.tenants import Tenant

        return Tenant.objects

    # ------------------------------------------------------------------ #
    # Read operations                                                      #
    # ------------------------------------------------------------------ #

    def get_by_id(self, tenant_id: int) -> TenantEntity | None:
        obj = self._qs.filter(pk=tenant_id).first()
        return _model_to_entity(obj) if obj else None

    def get_by_uuid(self, uuid_value: str) -> TenantEntity | None:
        try:
            parsed = uuid.UUID(str(uuid_value))
        except ValueError:
            return None
        obj = self._qs.filter(uuid=parsed).first()
        return _model_to_entity(obj) if obj else None

    def get_by_code(self, code: str) -> TenantEntity | None:
        obj = self._qs.filter(code=code.upper()).first()
        return _model_to_entity(obj) if obj else None

    def list(
        self,
        *,
        filters: dict[str, Any] | None = None,
        search: str | None = None,
        ordering: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[TenantEntity], int]:
        qs = self._qs.all()

        # Apply structured filters
        if filters:
            if filters.get("is_active") is not None:
                qs = qs.filter(is_active=filters["is_active"])
            if filters.get("plan"):
                qs = qs.filter(plan=filters["plan"])

        # Full-text search across code, name
        if search:
            qs = qs.filter(Q(code__icontains=search) | Q(name__icontains=search))

        total = qs.count()

        allowed_orderings = {
            "created_at",
            "-created_at",
            "name",
            "-name",
            "code",
            "-code",
            "plan",
            "-plan",
        }
        if ordering:
            safe_ordering = [o for o in ordering if o in allowed_orderings]
            if safe_ordering:
                qs = qs.order_by(*safe_ordering)

        items = [_model_to_entity(obj) for obj in qs[offset : offset + limit]]
        return items, total

    def exists_by_code(self, code: str, exclude_id: int | None = None) -> bool:
        qs = self._qs.filter(code=code.upper())
        if exclude_id:
            qs = qs.exclude(pk=exclude_id)
        return qs.exists()

    # ------------------------------------------------------------------ #
    # Write operations                                                     #
    # ------------------------------------------------------------------ #

    def create(self, entity: TenantEntity) -> TenantEntity:
        from tenants.models.tenants import Tenant

        obj = Tenant.objects.create(
            code=entity.code,
            name=entity.name,
            plan=entity.plan,
            is_active=entity.is_active,
            currency=entity.currency,
            exchange_rate=entity.exchange_rate,
            default_language=entity.default_language,
            timezone=entity.timezone,
            primary_color=entity.primary_color,
            max_users=entity.max_users,
            max_branches=entity.max_branches,
            max_vehicles=entity.max_vehicles,
            subscription_started_at=entity.subscription_started_at,
            subscription_expires_at=entity.subscription_expires_at,
            settings=entity.settings,
            domain=entity.domain,
            logo_url=entity.logo_url,
        )
        return _model_to_entity(obj)

    def update(self, entity: TenantEntity) -> TenantEntity:
        from tenants.models.tenants import Tenant

        Tenant.objects.filter(pk=entity.id).update(
            code=entity.code,
            name=entity.name,
            plan=entity.plan,
            is_active=entity.is_active,
            currency=entity.currency,
            exchange_rate=entity.exchange_rate,
            default_language=entity.default_language,
            timezone=entity.timezone,
            primary_color=entity.primary_color,
            max_users=entity.max_users,
            max_branches=entity.max_branches,
            max_vehicles=entity.max_vehicles,
            subscription_started_at=entity.subscription_started_at,
            subscription_expires_at=entity.subscription_expires_at,
            settings=entity.settings,
            domain=entity.domain,
            logo_url=entity.logo_url,
        )
        return self.get_by_id(entity.id)  # type: ignore[return-value]

    def delete(self, tenant_id: int) -> None:
        from tenants.models.tenants import Tenant

        Tenant.objects.filter(pk=tenant_id).delete()

    def deactivate(self, tenant_id: int) -> TenantEntity:
        from tenants.models.tenants import Tenant

        Tenant.objects.filter(pk=tenant_id).update(is_active=False)
        return self.get_by_id(tenant_id)  # type: ignore[return-value]
