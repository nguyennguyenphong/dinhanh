# ============================================================================
# FILE: apps/tenants/repositories/tenant_repository.py
# ============================================================================
from typing import Optional
from tenants.models.tenants import Tenant

class TenantRepository:
    """
    Handles encapsulation of database operations for the Tenant model.
    """
    @staticmethod
    def exists_by_code(code: str) -> bool:
        return Tenant.objects.filter(code__iexact=code).exists()

    @staticmethod
    def exists_by_domain(domain: str) -> bool:
        if not domain:
            return False
        return Tenant.objects.filter(domain__iexact=domain).exists()

    @staticmethod
    def create(data: dict) -> Tenant:
        """Persists the Tenant instance directly into the database."""
        return Tenant.objects.create(**data)

    @staticmethod
    def get_by_id(tenant_id: int) -> Optional[Tenant]:
        try:
            return Tenant.objects.get(pk=tenant_id)
        except Tenant.DoesNotExist:
            return None