from datetime import timedelta

import pytest
from django.utils import timezone

from tenants.application.dtos import TenantCreateDTO
from tenants.application.usecases import CreateTenantUseCase
from tenants.models.tenant_audit_log import TenantAuditLog
from tenants.models.tenants import Tenant
from tenants.serializers.tenants.tenant_create_serializer import TenantCreateSerializer
from tenants.serializers.tenants.tenant_update_serializer import TenantUpdateSerializer


class TestCreateTenantUseCase:
    def test_creates_tenant_successfully(self, make_entity, mock_repos):

        tenant_repo, audit_repo = mock_repos()
        tenant_repo.exists_by_code.return_value = False
        saved = make_entity()
        tenant_repo.create.return_value = saved

        uc = CreateTenantUseCase(tenant_repo, audit_repo)
        dto = TenantCreateDTO(code="DEMO", name="Demo Bus")
        result = uc.execute(dto, actor_id=1, actor_username="admin")

        assert result.code == "DEMO"


@pytest.mark.django_db
class TestTenantSerializers:
    def test_tenant_create_serializer_subscription_expires_at(self):
        start = timezone.now()
        expiry = start + timedelta(days=30)
        data = {
            "code": "TESTINC",
            "name": "Test Company",
            "plan": "STANDARD",
            "subscription_started_at": start.isoformat(),
            "subscription_expires_at": expiry.isoformat(),
        }
        serializer = TenantCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["subscription_expires_at"] is not None

    def test_tenant_update_serializer_subscription_expires_at(self):
        start = timezone.now()
        expiry = start + timedelta(days=30)
        data = {
            "code": "TESTINC",
            "name": "Test Company",
            "plan": "STANDARD",
            "subscription_started_at": start.isoformat(),
            "subscription_expires_at": expiry.isoformat(),
        }
        serializer = TenantUpdateSerializer(data=data, context={"tenant_id": 1})
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["subscription_expires_at"] is not None


@pytest.mark.django_db
class TestTenantSignals:
    def test_tenant_save_creates_audit_log(self):
        # Clean previous logs if any
        TenantAuditLog.objects.all().delete()
        Tenant.all_objects.all().delete()

        tenant = Tenant.objects.create(
            code="SIGNAL",
            name="Signal Test Company",
            plan="STANDARD",
            is_active=True,
        )

        # Signal should have fired and written a TenantAuditLog entry
        log = TenantAuditLog.objects.filter(tenant=tenant).first()
        assert log is not None
        assert log.action == "CREATE"
        assert log.module == "tenants.signals"

        # Update tenant and see if update signal fires
        tenant.name = "Updated Signal Test Company"
        tenant.save()

        log_update = TenantAuditLog.objects.filter(
            tenant=tenant, action="UPDATE"
        ).first()
        assert log_update is not None
        assert log_update.changes is not None
        assert "name" in log_update.changes
        assert log_update.changes["name"]["new"] == "Updated Signal Test Company"
