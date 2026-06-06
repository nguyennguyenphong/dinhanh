"""
Django ORM concrete implementations for:
  - TenantAuditLog
"""
from __future__ import annotations

from tenants.repositories.interfaces.tenant_audit_log_repository_interface import ITenantAuditLogRepository


class TenantAuditLogRepositoryImpl(ITenantAuditLogRepository):

    def create_log(
        self,
        *,
        tenant_id: int,
        user_id: int | None,
        username: str | None,
        action: str,
        module: str,
        object_type: str | None = None,
        object_id: str | None = None,
        object_repr: str | None = None,
        old_values: dict | None = None,
        new_values: dict | None = None,
        changes: dict | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        status: str = "SUCCESS",
        error_message: str | None = None,
    ) -> None:
        from tenants.models.tenent_audit_log import TenantAuditLog

        TenantAuditLog.objects.create(
            tenant_id=tenant_id,
            user_id=user_id,
            username=username,
            action=action,
            module=module,
            object_type=object_type,
            object_id=str(object_id) if object_id else None,
            object_repr=object_repr,
            old_values=old_values,
            new_values=new_values,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            error_message=error_message,
        )

    def list_by_tenant(
        self,
        tenant_id: int,
        *,
        action: str | None = None,
        module: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict], int]:
        from tenants.models.tenent_audit_log import TenantAuditLog

        qs = TenantAuditLog.objects.filter(tenant_id=tenant_id)
        if action:
            qs = qs.filter(action=action)
        if module:
            qs = qs.filter(module=module)

        total = qs.count()
        records = list(
            qs.values(
                "id",
                "user_id",
                "username",
                "action",
                "module",
                "object_type",
                "object_id",
                "object_repr",
                "old_values",
                "new_values",
                "changes",
                "ip_address",
                "status",
                "error_message",
                "created_at",
            )[offset: offset + limit]
        )
        return records, total
