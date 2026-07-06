"""
Use-cases for Tenant Init operations.
Each use-case class has a single public method and
orchestrates domain logic + repositories + audit logging.
"""

from __future__ import annotations

from typing import Any

from tenants.application.dtos.tenants.tenant_response_dto import TenantResponseDTO
from tenants.domain.entities.tenant_entity import (
    TenantEntity,
)


def _entity_to_response(entity: TenantEntity) -> TenantResponseDTO:
    return TenantResponseDTO(
        id=entity.id,  # type: ignore[arg-type]
        uuid=str(entity.uuid),
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
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def _entity_to_audit_values(entity: TenantEntity) -> dict[str, Any]:
    """Serialize entity fields for audit log storage."""
    return {
        "code": entity.code,
        "name": entity.name,
        "plan": entity.plan,
        "is_active": entity.is_active,
        "currency": entity.currency,
        "exchange_rate": str(entity.exchange_rate),
        "default_language": entity.default_language,
        "timezone": entity.timezone,
        "max_users": entity.max_users,
        "max_branches": entity.max_branches,
        "max_vehicles": entity.max_vehicles,
        "subscription_expires_at": (
            entity.subscription_expires_at.isoformat()
            if entity.subscription_expires_at
            else None
        ),
    }


def _compute_changes(old: dict, new: dict) -> dict[str, dict]:
    """Return only changed key/value pairs as {field: {old, new}}."""
    return {
        k: {"old": old.get(k), "new": new.get(k)}
        for k in set(old) | set(new)
        if old.get(k) != new.get(k)
    }
