"""
Unit tests for Tenant use-cases.
Uses unittest.mock to stub repositories — no database required.
"""
from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from tenants.application.dtos import (
    TenantCreateDTO,
    TenantListQueryDTO,
    TenantUpdateDTO,
)
from tenants.application.usecases import (
    CreateTenantUseCase,
    DeactivateTenantUseCase,
    GetTenantUseCase,
    ListTenantsUseCase,
    UpdateTenantUseCase,
)
from tenants.domain.entities import TenantEntity
from tenants.exceptions import (
    TenantAlreadyExistsError,
    TenantNotFoundError,
)


# =========================================================================== #
# Fixtures                                                                     #
# =========================================================================== #


def make_entity(**kwargs) -> TenantEntity:
    defaults = dict(
        id=1,
        uuid=uuid.uuid4(),
        code="DEMO",
        name="Demo Bus",
        plan="STANDARD",
        is_active=True,
        currency="VND",
        exchange_rate=Decimal("1.0000"),
        default_language="vi",
        timezone="Asia/Ho_Chi_Minh",
        primary_color="#3B82F6",
        max_users=10,
        max_branches=1,
        max_vehicles=50,
        subscription_started_at=None,
        subscription_expires_at=None,
        settings={},
        domain=None,
        logo_url=None,
    )
    defaults.update(kwargs)
    return TenantEntity(**defaults)


def mock_repos():
    tenant_repo = MagicMock()
    audit_repo = MagicMock()
    return tenant_repo, audit_repo


# =========================================================================== #
# CreateTenantUseCase                                                          #
# =========================================================================== #


class TestCreateTenantUseCase:
    def test_creates_tenant_successfully(self):
        tenant_repo, audit_repo = mock_repos()
        tenant_repo.exists_by_code.return_value = False
        saved = make_entity()
        tenant_repo.create.return_value = saved

        uc = CreateTenantUseCase(tenant_repo, audit_repo)
        dto = TenantCreateDTO(code="DEMO", name="Demo Bus")
        result = uc.execute(dto, actor_id=1, actor_username="admin")

        tenant_repo.create.assert_called_once()
        audit_repo.create_log.assert_called_once()
        assert result.code == "DEMO"

    def test_raises_when_code_already_exists(self):
        tenant_repo, audit_repo = mock_repos()
        tenant_repo.exists_by_code.return_value = True

        uc = CreateTenantUseCase(tenant_repo, audit_repo)
        dto = TenantCreateDTO(code="DEMO", name="Demo Bus")

        with pytest.raises(TenantAlreadyExistsError):
            uc.execute(dto)

        tenant_repo.create.assert_not_called()
        audit_repo.create_log.assert_not_called()

    def test_code_is_uppercased(self):
        tenant_repo, audit_repo = mock_repos()
        tenant_repo.exists_by_code.return_value = False
        saved = make_entity(code="LOWERCASE")
        tenant_repo.create.return_value = saved

        uc = CreateTenantUseCase(tenant_repo, audit_repo)
        dto = TenantCreateDTO(code="lowercase", name="Test")
        uc.execute(dto)

        call_args = tenant_repo.create.call_args[0][0]
        assert call_args.code == "LOWERCASE"

    def test_plan_limits_applied_from_plan_definition(self):
        tenant_repo, audit_repo = mock_repos()
        tenant_repo.exists_by_code.return_value = False
        tenant_repo.create.return_value = make_entity(plan="PROFESSIONAL")

        uc = CreateTenantUseCase(tenant_repo, audit_repo)
        dto = TenantCreateDTO(code="ACME", name="ACME Bus", plan="PROFESSIONAL")
        uc.execute(dto)

        entity_arg = tenant_repo.create.call_args[0][0]
        assert entity_arg.max_users == 50
        assert entity_arg.max_branches == 5
        assert entity_arg.max_vehicles == 200


# =========================================================================== #
# GetTenantUseCase                                                             #
# =========================================================================== #


class TestGetTenantUseCase:
    def test_returns_tenant_by_id(self):
        tenant_repo = MagicMock()
        tenant_repo.get_by_id.return_value = make_entity()
        uc = GetTenantUseCase(tenant_repo)
        result = uc.by_id(1)
        assert result.id == 1

    def test_raises_not_found_for_missing_id(self):
        tenant_repo = MagicMock()
        tenant_repo.get_by_id.return_value = None
        uc = GetTenantUseCase(tenant_repo)
        with pytest.raises(TenantNotFoundError):
            uc.by_id(999)

    def test_returns_tenant_by_code(self):
        tenant_repo = MagicMock()
        tenant_repo.get_by_code.return_value = make_entity(code="XYZ")
        uc = GetTenantUseCase(tenant_repo)
        result = uc.by_code("XYZ")
        assert result.code == "XYZ"


# =========================================================================== #
# ListTenantsUseCase                                                           #
# =========================================================================== #


class TestListTenantsUseCase:
    def test_returns_paginated_results(self):
        tenant_repo = MagicMock()
        entities = [make_entity(id=i, code=f"T{i:03d}") for i in range(1, 6)]
        tenant_repo.list.return_value = (entities, 5)

        uc = ListTenantsUseCase(tenant_repo)
        query = TenantListQueryDTO(limit=5, offset=0)
        items, total = uc.execute(query)

        assert total == 5
        assert len(items) == 5

    def test_passes_filters_to_repo(self):
        tenant_repo = MagicMock()
        tenant_repo.list.return_value = ([], 0)

        uc = ListTenantsUseCase(tenant_repo)
        query = TenantListQueryDTO(plan="ENTERPRISE", is_active=True)
        uc.execute(query)

        call_kwargs = tenant_repo.list.call_args.kwargs
        assert call_kwargs["filters"]["plan"] == "ENTERPRISE"
        assert call_kwargs["filters"]["is_active"] is True


# =========================================================================== #
# UpdateTenantUseCase                                                          #
# =========================================================================== #


class TestUpdateTenantUseCase:
    def test_updates_name(self):
        tenant_repo, audit_repo = mock_repos()
        original = make_entity(name="Old Name")
        updated = make_entity(name="New Name")
        tenant_repo.get_by_id.return_value = original
        tenant_repo.update.return_value = updated

        uc = UpdateTenantUseCase(tenant_repo, audit_repo)
        dto = TenantUpdateDTO(tenant_id=1, name="New Name")
        result = uc.execute(dto, actor_id=1)

        assert result.name == "New Name"
        audit_repo.create_log.assert_called_once()

    def test_raises_not_found(self):
        tenant_repo, audit_repo = mock_repos()
        tenant_repo.get_by_id.return_value = None

        uc = UpdateTenantUseCase(tenant_repo, audit_repo)
        dto = TenantUpdateDTO(tenant_id=999, name="X")

        with pytest.raises(TenantNotFoundError):
            uc.execute(dto)


# =========================================================================== #
# DeactivateTenantUseCase                                                      #
# =========================================================================== #


class TestDeactivateTenantUseCase:
    def test_deactivates_tenant(self):
        tenant_repo, audit_repo = mock_repos()
        tenant_repo.get_by_id.return_value = make_entity()
        tenant_repo.deactivate.return_value = make_entity(is_active=False)

        uc = DeactivateTenantUseCase(tenant_repo, audit_repo)
        result = uc.execute(1, actor_id=1)

        tenant_repo.deactivate.assert_called_once_with(1)
        assert result.is_active is False

    def test_raises_not_found(self):
        tenant_repo, audit_repo = mock_repos()
        tenant_repo.get_by_id.return_value = None

        uc = DeactivateTenantUseCase(tenant_repo, audit_repo)
        with pytest.raises(TenantNotFoundError):
            uc.execute(999)


# =========================================================================== #
# TenantEntity domain tests                                                    #
# =========================================================================== #


class TestTenantEntityDomain:
    def test_can_add_user_within_limit(self):
        entity = make_entity(max_users=5)
        assert entity.can_add_user(4) is True
        assert entity.can_add_user(5) is False

    def test_trial_expired_when_no_expiry(self):
        from django.utils import timezone
        entity = make_entity(plan="TRIAL", subscription_expires_at=None)
        assert entity.is_trial_expired(timezone.now()) is True

    def test_non_trial_never_expired(self):
        from django.utils import timezone
        entity = make_entity(plan="STANDARD", subscription_expires_at=None)
        assert entity.is_trial_expired(timezone.now()) is False

    def test_has_feature_via_plan(self):
        entity = make_entity(plan="PROFESSIONAL")
        assert entity.has_feature("api") is True
        assert entity.has_feature("advanced_analytics") is False

    def test_enterprise_has_all_features(self):
        entity = make_entity(plan="ENTERPRISE")
        assert entity.has_feature("any_random_feature") is True