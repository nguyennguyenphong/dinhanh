"""
Domain entities for Tenant bounded context.
Pure Python dataclasses — no Django ORM dependency here.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class TenantPlan:
    code: str
    max_users: int
    max_branches: int
    max_vehicles: int
    features: list[str]

    PLANS: dict[str, "TenantPlan"] = field(default_factory=dict, init=False, repr=False)

    def has_feature(self, feature: str) -> bool:
        return "all" in self.features or feature in self.features


TENANT_PLANS: dict[str, TenantPlan] = {
    "TRIAL": TenantPlan(
        code="TRIAL",
        max_users=3,
        max_branches=1,
        max_vehicles=10,
        features=["basic_ticketing", "basic_reporting"],
    ),
    "STANDARD": TenantPlan(
        code="STANDARD",
        max_users=10,
        max_branches=1,
        max_vehicles=50,
        features=["ticketing", "hr", "basic_cargo", "reporting"],
    ),
    "PROFESSIONAL": TenantPlan(
        code="PROFESSIONAL",
        max_users=50,
        max_branches=5,
        max_vehicles=200,
        features=["ticketing", "hr", "cargo", "reporting", "api"],
    ),
    "ENTERPRISE": TenantPlan(
        code="ENTERPRISE",
        max_users=999,
        max_branches=999,
        max_vehicles=9999,
        features=["all"],
    ),
}


@dataclass
class TenantEntity:
    """
    Domain representation of a Tenant.
    Holds business rules independent of persistence layer.
    """

    id: int | None
    uuid: uuid.UUID
    code: str
    name: str
    plan: str
    is_active: bool
    currency: str
    exchange_rate: Decimal
    default_language: str
    timezone: str
    primary_color: str
    max_users: int
    max_branches: int
    max_vehicles: int
    subscription_started_at: datetime | None
    subscription_expires_at: datetime | None
    settings: dict[str, Any]
    domain: str | None = None
    logo_url: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # ------------------------------------------------------------------ #
    # Business rules                                                       #
    # ------------------------------------------------------------------ #

    def get_plan_definition(self) -> TenantPlan | None:
        return TENANT_PLANS.get(self.plan)

    def is_subscription_active(self, now: datetime) -> bool:
        if not self.subscription_expires_at:
            return True
        return now <= self.subscription_expires_at

    def is_trial_expired(self, now: datetime) -> bool:
        if self.plan != "TRIAL":
            return False
        if not self.subscription_expires_at:
            return True
        return now > self.subscription_expires_at

    def can_add_user(self, current_user_count: int) -> bool:
        return current_user_count < self.max_users

    def can_add_branch(self, current_branch_count: int) -> bool:
        return current_branch_count < self.max_branches

    def can_add_vehicle(self, current_vehicle_count: int) -> bool:
        return current_vehicle_count < self.max_vehicles

    def has_feature(self, feature: str) -> bool:
        plan_def = self.get_plan_definition()
        if not plan_def:
            return False
        return plan_def.has_feature(feature)
