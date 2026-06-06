"""
DRF API views for Tenant CRUD operations.

Endpoint map (wired in urls/tenant_urls.py):
    GET    /tenants/                -> TenantListView
"""
from __future__ import annotations

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from tenants.application.dtos import TenantListQueryDTO
from tenants.exceptions.exception import TenantDomainError
from tenants.policies import TenantPolicy
from tenants.providers import TenantProvider
from tenants.serializers import (
    TenantListQuerySerializer,
    TenantResponseSerializer,
)

from views.helpers.view_helpers import domain_error_response, paginated_response


class TenantListView(APIView):
    """
    GET  /tenants/   — list tenants with filter/search/pagination
    """

    def get(self, request: Request) -> Response:
        TenantPolicy.can_list(request)

        query_ser = TenantListQuerySerializer(data=request.query_params)
        query_ser.is_valid(raise_exception=True)
        data = query_ser.validated_data

        query_dto = TenantListQueryDTO(
            search=data.get("search"),
            plan=data.get("plan"),
            is_active=data.get("is_active"),
            ordering=data.get("ordering", ["-created_at"]),
            limit=data["limit"],
            offset=data["offset"],
        )

        try:
            items, total = TenantProvider.list_tenants().execute(query_dto)
        except TenantDomainError as exc:
            return domain_error_response(exc)

        return paginated_response(
            data=[vars(item) for item in items],
            total=total,
            limit=query_dto.limit,
            offset=query_dto.offset,
            serializer_class=TenantResponseSerializer,
        )

