"""
DRF API views for:
  - TenantFeatureFlag  (/tenants/<pk>/feature-flags/)
  - TenantInvitation   (/tenants/<pk>/invitations/)
  - TenantAuditLog     (/tenants/<pk>/audit-logs/)
"""

from __future__ import annotations

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from tenants.application.dtos import TenantAuditLogQueryDTO
from tenants.exceptions.exception import TenantDomainError
from tenants.policies import TenantPolicy
from tenants.providers import TenantProvider
from tenants.serializers.tenant_audit_log import (
    TenantAuditLogQuerySerializer,
    TenantAuditLogResponseSerializer,
)
from tenants.views.helpers.view_helpers import domain_error_response, paginated_response


class TenantAuditLogListView(APIView):
    """
    GET /tenants/<pk>/audit-logs/
    """

    def get(self, request: Request, pk: int) -> Response:
        TenantPolicy.can_read_audit_logs(request, pk)

        query_ser = TenantAuditLogQuerySerializer(data=request.query_params)
        query_ser.is_valid(raise_exception=True)
        vd = query_ser.validated_data

        dto = TenantAuditLogQueryDTO(
            tenant_id=pk,
            action=vd.get("action"),
            module=vd.get("module"),
            limit=vd["limit"],
            offset=vd["offset"],
        )

        try:
            records, total = TenantProvider.list_audit_logs().execute(dto)
        except TenantDomainError as exc:
            return domain_error_response(exc)

        return paginated_response(
            data=records,
            total=total,
            limit=dto.limit,
            offset=dto.offset,
            serializer_class=TenantAuditLogResponseSerializer,
        )
