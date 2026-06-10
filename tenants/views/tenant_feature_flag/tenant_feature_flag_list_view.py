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

from tenants.application.dtos import UpsertTenantFeatureFlagDTO
from tenants.exceptions.exception import TenantDomainError
from tenants.policies import TenantPolicy
from tenants.providers import TenantProvider
from tenants.serializers.tenant_feature_flags import (
    TenantFeatureFlagResponseSerializer,
    TenantFeatureFlagUpsertSerializer,
)
from tenants.views.helpers.view_helpers import RequestContext, domain_error_response

# =========================================================================== #
# Feature Flags                                                                #
# =========================================================================== #


class TenantFeatureFlagListView(APIView):
    """
    GET  /tenants/<pk>/feature-flags/
    POST /tenants/<pk>/feature-flags/
    """

    def get(self, request: Request, pk: int) -> Response:
        TenantPolicy.can_manage_feature_flags(request, pk)

        try:
            flags = TenantProvider.list_feature_flags().execute(pk)
        except TenantDomainError as exc:
            return domain_error_response(exc)

        data = [vars(f) for f in flags]
        serializer = TenantFeatureFlagResponseSerializer(data, many=True)
        return Response(serializer.data)

    def post(self, request: Request, pk: int) -> Response:
        TenantPolicy.can_manage_feature_flags(request, pk)

        serializer = TenantFeatureFlagUpsertSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data

        ctx = RequestContext.from_request(request)
        dto = UpsertTenantFeatureFlagDTO(tenant_id=pk, **vd)

        try:
            saved = TenantProvider.upsert_feature_flag().execute(
                dto,
                actor_id=ctx.actor_id,
                actor_username=ctx.actor_username,
                ip_address=ctx.ip_address,
                user_agent=ctx.user_agent,
            )
        except TenantDomainError as exc:
            return domain_error_response(exc)

        return Response(
            TenantFeatureFlagResponseSerializer(vars(saved)).data,
            status=status.HTTP_201_CREATED,
        )
