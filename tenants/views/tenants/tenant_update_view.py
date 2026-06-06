"""
DRF API views for Tenant CRUD operations.

Endpoint map (wired in urls/tenant_urls.py):
    PATCH  /tenants/<pk>/  — partial update
"""
from __future__ import annotations

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from tenants.application.dtos import TenantUpdateDTO
from tenants.exceptions.exception import TenantDomainError
from tenants.policies import TenantPolicy
from tenants.providers import TenantProvider
from tenants.serializers import (
    TenantResponseSerializer,
    TenantUpdateSerializer,
)

from views.helpers.view_helpers import RequestContext, domain_error_response, paginated_response



class TenantUpdateView(APIView):
    """
    PATCH  /tenants/<pk>/  — partial update
    """

    def patch(self, request: Request, pk: int) -> Response:
        TenantPolicy.can_update(request, pk)

        serializer = TenantUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data

        ctx = RequestContext.from_request(request)
        dto = TenantUpdateDTO(tenant_id=pk, **vd)

        try:
            result = TenantProvider.update_tenant().execute(
                dto,
                actor_id=ctx.actor_id,
                actor_username=ctx.actor_username,
                ip_address=ctx.ip_address,
                user_agent=ctx.user_agent,
            )
        except TenantDomainError as exc:
            return domain_error_response(exc)

        return Response(TenantResponseSerializer(vars(result)).data)
