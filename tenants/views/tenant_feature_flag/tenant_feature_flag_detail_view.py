"""
DRF API views for:
  - TenantFeatureFlag  (/tenants/<pk>/feature-flags/)
  - TenantInvitation   (/tenants/<pk>/invitations/)
  - TenantAuditLog     (/tenants/<pk>/audit-logs/)
"""

from __future__ import annotations

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from tenants.exceptions.exception import TenantDomainError
from tenants.policies import TenantPolicy
from tenants.providers import TenantProvider
from tenants.views.helpers.view_helpers import RequestContext, domain_error_response


class TenantFeatureFlagDetailView(APIView):
    """
    DELETE /tenants/<pk>/feature-flags/<code>/
    """

    def delete(self, request: Request, pk: int, code: str) -> Response:
        TenantPolicy.can_manage_feature_flags(request, pk)

        ctx = RequestContext.from_request(request)

        try:
            TenantProvider.delete_feature_flag().execute(
                pk,
                code,
                actor_id=ctx.actor_id,
                actor_username=ctx.actor_username,
                ip_address=ctx.ip_address,
                user_agent=ctx.user_agent,
            )
        except TenantDomainError as exc:
            return domain_error_response(exc)

        return Response(status=status.HTTP_204_NO_CONTENT)
