from typing import Optional
from django.db.models import QuerySet

from tenants.models.tenent_feature_flag import TenantFeatureFlag


class TenantFeatureFlagRepository:

    @staticmethod
    def get_flags_for_tenant(tenant_id: int) -> QuerySet[TenantFeatureFlag]:
        return TenantFeatureFlag.objects.filter(tenant_id=tenant_id)

    @staticmethod
    def get_by_tenant_and_code(tenant_id: int, code: str) -> Optional[TenantFeatureFlag]:
        return TenantFeatureFlag.objects.filter(tenant_id=tenant_id, code=code).first()

    @staticmethod
    def create(data: dict) -> TenantFeatureFlag:
        return TenantFeatureFlag.objects.create(**data)