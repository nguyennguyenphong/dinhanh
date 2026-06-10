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

from tenants.application.dtos import CreateTenantInvitationDTO
from tenants.exceptions import TenantDomainError
from tenants.policies import TenantPolicy
from tenants.providers import TenantProvider
from tenants.serializers import (
    TenantInvitationCreateSerializer,
    TenantInvitationResponseSerializer,
)
from tenants.views.helpers.view_helpers import (
    RequestContext,
    domain_error_response,
    paginated_response,
)


class TenantInvitationCreateView(APIView):
    """
    GET  /tenants/<pk>/invitations/
    POST /tenants/<pk>/invitations/
    """

    def post(self, request: Request, pk: int) -> Response:
        TenantPolicy.can_manage_invitations(request, pk)

        serializer = TenantInvitationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data

        ctx = RequestContext.from_request(request)
        dto = CreateTenantInvitationDTO(
            tenant_id=pk,
            email=vd["email"],
            invited_by_id=ctx.actor_id or 0,
            expires_in_days=vd.get("expires_in_days", 7),
        )

        try:
            saved = TenantProvider.create_invitation().execute(
                dto,
                actor_username=ctx.actor_username,
                ip_address=ctx.ip_address,
                user_agent=ctx.user_agent,
            )
        except TenantDomainError as exc:
            return domain_error_response(exc)

        return Response(
            TenantInvitationResponseSerializer(vars(saved)).data,
            status=status.HTTP_201_CREATED,
        )
