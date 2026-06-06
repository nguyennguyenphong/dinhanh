"""
TenantService — high-level service facade.

Purpose: provides a clean Python API that other Django apps (not views)
can call without knowing about DTOs or repositories. Views should prefer
TenantProvider + use-cases directly; this layer is for inter-app use.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from tenants.application.dtos import (
    TenantListQueryDTO,
    TenantResponseDTO,
    TenantCreateDTO,
    TenantUpdateDTO,
)
from tenants.application.dtos.tenant_feature_flags import UpsertTenantFeatureFlagDTO
from tenants.domain.entities import TenantFeatureFlagEntity
from tenants.providers import TenantProvider


class TenantService:

    # ------------------------------------------------------------------ #
    # Tenant CRUD                                                          #
    # ------------------------------------------------------------------ #

    @staticmethod
    def create(
        *,
        code: str,
        name: str,
        plan: str = "STANDARD",
        currency: str = "VND",
        exchange_rate: Decimal = Decimal("1.0000"),
        default_language: str = "vi",
        timezone: str = "Asia/Ho_Chi_Minh",
        primary_color: str = "#3B82F6",
        settings: dict[str, Any] | None = None,
        domain: str | None = None,
        logo_url: str | None = None,
        actor_id: int | None = None,
        actor_username: str | None = None,
    ) -> TenantResponseDTO:
        dto = TenantCreateDTO(
            code=code,
            name=name,
            plan=plan,
            currency=currency,
            exchange_rate=exchange_rate,
            default_language=default_language,
            timezone=timezone,
            primary_color=primary_color,
            settings=settings or {},
            domain=domain,
            logo_url=logo_url,
        )
        return TenantProvider.create_tenant().execute(
            dto, actor_id=actor_id, actor_username=actor_username
        )

    @staticmethod
    def get(tenant_id: int) -> TenantResponseDTO:
        return TenantProvider.get_tenant().by_id(tenant_id)

    @staticmethod
    def get_by_code(code: str) -> TenantResponseDTO:
        return TenantProvider.get_tenant().by_code(code)

    @staticmethod
    def list(
        *,
        search: str | None = None,
        plan: str | None = None,
        is_active: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[TenantResponseDTO], int]:
        query = TenantListQueryDTO(
            search=search,
            plan=plan,
            is_active=is_active,
            limit=limit,
            offset=offset,
        )
        return TenantProvider.list_tenants().execute(query)

    @staticmethod
    def update(tenant_id: int, **fields: Any) -> TenantResponseDTO:
        dto = TenantUpdateDTO(tenant_id=tenant_id, **fields)
        return TenantProvider.update_tenant().execute(dto)

    @staticmethod
    def deactivate(tenant_id: int, actor_id: int | None = None) -> TenantResponseDTO:
        return TenantProvider.deactivate_tenant().execute(
            tenant_id, actor_id=actor_id
        )

    # ------------------------------------------------------------------ #
    # Feature flags                                                        #
    # ------------------------------------------------------------------ #

    @staticmethod
    def set_feature_flag(
        tenant_id: int,
        code: str,
        name: str,
        is_enabled: bool,
        rollout_percentage: int = 100,
        config: dict[str, Any] | None = None,
    ) -> TenantFeatureFlagEntity:
        dto = UpsertTenantFeatureFlagDTO(
            tenant_id=tenant_id,
            code=code,
            name=name,
            is_enabled=is_enabled,
            rollout_percentage=rollout_percentage,
            config=config or {},
        )
        return TenantProvider.upsert_feature_flag().execute(dto)

    @staticmethod
    def is_feature_enabled(tenant_id: int, code: str) -> bool:
        """
        Quick check for use in business logic across the codebase.
        Returns False if the flag doesn't exist.
        """
        flags = TenantProvider.list_feature_flags().execute(tenant_id)
        for flag in flags:
            if flag.code == code.upper():
                return flag.is_enabled
        return False