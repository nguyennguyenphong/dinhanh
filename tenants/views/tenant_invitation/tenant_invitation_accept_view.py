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

from tenants.application.dtos import AcceptTenantInvitationDTO
from tenants.exceptions.exception import TenantDomainError
from tenants.providers import TenantProvider
from tenants.serializers import (
    TenantInvitationAcceptSerializer,
    TenantInvitationResponseSerializer,
)

from tenants.views.helpers.view_helpers import RequestContext, domain_error_response



class TenantInvitationAcceptView(APIView):
    """
    POST /invitations/accept/   — public endpoint, no auth required
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request: Request) -> Response:
        serializer = TenantInvitationAcceptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ctx = RequestContext.from_request(request)
        dto = AcceptTenantInvitationDTO(token=serializer.validated_data["token"])

        try:
            saved = TenantProvider.accept_invitation().execute(
                dto,
                ip_address=ctx.ip_address,
                user_agent=ctx.user_agent,
            )
        except TenantDomainError as exc:
            return domain_error_response(exc)

        return Response(TenantInvitationResponseSerializer(vars(saved)).data)