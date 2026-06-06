"""
Abstract repository interfaces for the Tenant Audit Log bounded context.
Concrete implementations live in repositories/implement/.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

class ITenantAuditLogRepository(ABC):
    """Contract for audit log persistence."""

    @abstractmethod
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
        ...

    @abstractmethod
    def list_by_tenant(
        self,
        tenant_id: int,
        *,
        action: str | None = None,
        module: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[dict], int]:
        ...