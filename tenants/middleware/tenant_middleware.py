"""
TenantMiddleware — resolves the current tenant from the request and attaches
it to the request object so views/services can reference it without re-querying.

Resolution order:
  1. X-Tenant-Code header  (for API clients)
  2. Subdomain             (e.g. dinhanh.buscms.vn → code=DINHANH)
  3. request.user.tenant_id (if user model has tenant FK)

Attach to MIDDLEWARE in settings.py AFTER AuthenticationMiddleware.
"""

from __future__ import annotations

import logging

from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

# Paths that should not require a resolved tenant
_EXEMPT_PREFIXES = (
    "/admin/",
    "/api/v1/invitations/accept/",
    "/health/",
    "/static/",
    "/media/",
)


class TenantMiddleware(MiddlewareMixin):
    """
    Resolves the active tenant and stores:
        request.tenant        — Tenant ORM instance or None
        request.tenant_id     — int or None
        request.tenant_code   — str or None
    """

    def process_request(self, request: HttpRequest) -> HttpResponse | None:
        request.tenant = None
        request.tenant_id = None
        request.tenant_code = None

        if self._is_exempt(request):
            return None

        tenant = (
            self._resolve_from_header(request)
            or self._resolve_from_subdomain(request)
            or self._resolve_from_user(request)
        )

        if tenant:
            request.tenant = tenant
            request.tenant_id = tenant.pk
            request.tenant_code = tenant.code

        return None

    # ------------------------------------------------------------------ #
    # Resolution strategies                                                #
    # ------------------------------------------------------------------ #

    def _resolve_from_header(self, request: HttpRequest):
        code = request.META.get("HTTP_X_TENANT_CODE", "").strip().upper()
        if not code:
            return None
        return self._get_active_tenant_by_code(code)

    def _resolve_from_subdomain(self, request: HttpRequest):
        host = request.get_host().split(":")[0]  # strip port
        parts = host.split(".")
        if len(parts) < 3:
            # Not a subdomain URL (e.g. localhost)
            return None
        subdomain = parts[0].upper()
        return self._get_active_tenant_by_code(subdomain)

    def _resolve_from_user(self, request: HttpRequest):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return None
        tenant_id = getattr(user, "tenant_id", None)
        if not tenant_id:
            return None
        return self._get_active_tenant_by_id(tenant_id)

    # ------------------------------------------------------------------ #
    # DB helpers                                                           #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _get_active_tenant_by_code(code: str):
        try:
            from tenants.models.tenants import Tenant

            return Tenant.objects.filter(code=code, is_active=True).first()
        except Exception:
            logger.exception("Error resolving tenant by code=%s", code)
            return None

    @staticmethod
    def _get_active_tenant_by_id(tenant_id: int):
        try:
            from tenants.models.tenants import Tenant

            return Tenant.objects.filter(pk=tenant_id, is_active=True).first()
        except Exception:
            logger.exception("Error resolving tenant by id=%s", tenant_id)
            return None

    @staticmethod
    def _is_exempt(request: HttpRequest) -> bool:
        return any(request.path.startswith(prefix) for prefix in _EXEMPT_PREFIXES)
