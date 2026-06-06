"""
DRF API views for Tenant CRUD operations.

Endpoint map (wired in urls/tenant_urls.py):
    GET    /tenants/<pk>/           -> TenantDetailView
"""
from __future__ import annotations

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from tenants.exceptions.exception import TenantDomainError
from tenants.policies import TenantPolicy
from tenants.providers import TenantProvider
from views.helpers.view_helpers import RequestContext, domain_error_response, paginated_response



class TenantSoftDeleteView(APIView):
    """
    DELETE /tenants/<pk>/  — soft deactivate
    """

    def delete(self, request: Request, pk: int) -> Response:
        TenantPolicy.can_deactivate(request)

        ctx = RequestContext.from_request(request)

        try:
            TenantProvider.deactivate_tenant().execute(
                pk,
                actor_id=ctx.actor_id,
                actor_username=ctx.actor_username,
                ip_address=ctx.ip_address,
                user_agent=ctx.user_agent,
            )
        except TenantDomainError as exc:
            return domain_error_response(exc)

        return Response(status=status.HTTP_204_NO_CONTENT)