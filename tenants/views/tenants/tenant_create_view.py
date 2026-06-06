"""
DRF API views for Tenant CRUD operations.

Endpoint map (wired in urls/tenant_urls.py):
    POST   /tenants/                -> TenantListView
"""
from __future__ import annotations

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from tenants.application.dtos import TenantUpdateDTO
from tenants.exceptions.exception import TenantDomainError
from tenants.policies import TenantPolicy
from tenants.providers import TenantProvider
from tenants.serializers import (
    TenantCreateSerializer,
    TenantResponseSerializer,
)

from views.helpers.view_helpers import RequestContext, domain_error_response


class TenantCreateView(APIView):
    """
    POST /tenants/   — create a new tenant
    """

    def post(self, request: Request) -> Response:
        TenantPolicy.can_create(request)

        serializer = TenantCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data

        ctx = RequestContext.from_request(request)
        dto = TenantUpdateDTO(
            code=vd["code"],
            name=vd["name"],
            plan=vd.get("plan", "STANDARD"),
            currency=vd.get("currency", "VND"),
            exchange_rate=vd.get("exchange_rate"),
            default_language=vd.get("default_language", "vi"),
            timezone=vd.get("timezone", "Asia/Ho_Chi_Minh"),
            primary_color=vd.get("primary_color", "#3B82F6"),
            domain=vd.get("domain"),
            logo_url=vd.get("logo_url"),
            subscription_started_at=vd.get("subscription_started_at"),
            subscription_expires_at=vd.get("subscription_expires_at"),
            settings=vd.get("settings", {}),
            is_active=vd.get("is_active", True),
        )

        try:
            result = TenantProvider.create_tenant().execute(
                dto,
                actor_id=ctx.actor_id,
                actor_username=ctx.actor_username,
                ip_address=ctx.ip_address,
                user_agent=ctx.user_agent,
            )
        except TenantDomainError as exc:
            return domain_error_response(exc)

        response_ser = TenantResponseSerializer(vars(result))
        return Response(response_ser.data, status=status.HTTP_201_CREATED)
