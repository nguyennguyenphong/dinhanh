from dataclasses import asdict
from django.db import transaction
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError

from tenants.models.tenants import Tenant
from tenants.models.tenent_audit_log import TenantAuditLog
from tenants.repositories.tenants.tenant_repository import TenantRepository
from tenants.dtos.tenants.tenant_create_dto import TenantCreateDTO
from tenants.dtos.tenants.tenant_update_dto import TenantUpdateDTO
from tenants.serializers.tenants.tenant_serializer import TenantSerializer


class TenantService:

    def __init__(self):
        self.repo = TenantRepository()

    @transaction.atomic
    def create_tenant(self, dto: TenantCreateDTO, requested_by_user) -> Tenant:
        """Handles explicit setup workflow of a business entity."""
        # Check uniqueness constraint
        if self.repo.get_by_code(dto.code):
            raise ValidationError({"code": "Tenant with this code already exists."})

        data = asdict(dto)
        tenant = self.repo.create(data)

        # Log Mutation Actions via Audit Trail
        self._write_audit_log(
            tenant=tenant,
            user=requested_by_user,
            action="CREATE",
            new_values=data
        )
        return tenant

    @transaction.atomic
    def update_tenant(self, tenant_id: int, dto: TenantUpdateDTO, requested_by_user) -> Tenant:
        tenant = self.repo.get_by_id(tenant_id)
        if not tenant:
            raise ValidationError("Tenant target not found.")

        old_values = TenantSerializer(tenant).data
        data_to_update = {k: v for k, v in asdict(dto).items() if v is not None}

        updated_tenant = self.repo.update(tenant, data_to_update)
        new_values = TenantSerializer(updated_tenant).data

        # Log changes delta calculation
        changes = {k: v for k, v in data_to_update.items() if old_values.get(k) != v}

        self._write_audit_log(
            tenant=updated_tenant,
            user=requested_by_user,
            action="UPDATE",
            old_values=old_values,
            new_values=new_values,
            changes=changes
        )
        return updated_tenant

    @transaction.atomic
    def delete_tenant(self, tenant_id: int, requested_by_user) -> bool:
        tenant = self.repo.get_by_id(tenant_id)
        if not tenant:
            raise ValidationError("Tenant not found to process elimination.")

        old_values = TenantSerializer(tenant).data
        self.repo.delete(tenant)

        # Audit trailing before complete cleanup execution contexts
        TenantAuditLog.objects.create(
            tenant_id=tenant_id,
            user_id=getattr(requested_by_user, 'id', None),
            username=getattr(requested_by_user, 'username', 'system'),
            action="DELETE",
            module="TENANT",
            object_type="Tenant",
            object_id=str(tenant_id),
            old_values=old_values,
            status="SUCCESS"
        )
        return True

    def _write_audit_log(self, tenant, user, action, old_values=None, new_values=None, changes=None):
        """Helper routing to construct persistent operational history tracking."""
        TenantAuditLog.objects.create(
            tenant=tenant,
            user_id=getattr(user, 'id', None),
            username=getattr(user, 'username', 'system'),
            action=action,
            module="TENANT",
            object_type="Tenant",
            object_id=str(tenant.id),
            object_repr=str(tenant),
            old_values=old_values,
            new_values=new_values,
            changes=changes,
            status="SUCCESS"
        )