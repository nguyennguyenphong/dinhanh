from typing import Optional, Tuple
from django.db.models import QuerySet

from tenants.models.tenants import Tenant


class TenantRepositoryImpl:

    @staticmethod
    def get_all_active() -> QuerySet[Tenant]:
        """Retrieve all active tenants."""
        return Tenant.objects.filter(is_active=True)

    @staticmethod
    def get_by_id(tenant_id: int) -> Optional[Tenant]:
        """Fetch tenant by ID."""
        try:
            return Tenant.objects.get(pk=tenant_id)
        except Tenant.DoesNotExist:
            return None

    @staticmethod
    def get_by_uuid(uuid_val: str) -> Optional[Tenant]:
        """Fetch tenant by UUID safely."""
        try:
            return Tenant.objects.get(uuid=uuid_val)
        except Tenant.DoesNotExist:
            return None

    @staticmethod
    def get_by_code(code: str) -> Optional[Tenant]:
        """Fetch tenant by Unique Code."""
        try:
            return Tenant.objects.get(code=code)
        except Tenant.DoesNotExist:
            return None

    @staticmethod
    def create(data: dict) -> Tenant:
        """Create a new Tenant entry."""
        return Tenant.objects.create(**data)

    @staticmethod
    def update(tenant: Tenant, data: dict) -> Tenant:
        """Update fields dynamically on execution."""
        for field, value in data.items():
            if value is not None:
                setattr(tenant, field, value)
        tenant.save()
        return tenant

    @staticmethod
    def delete(tenant: Tenant) -> Tuple[int, dict]:
        """Delete instance or hard-delete."""
        return tenant.delete()