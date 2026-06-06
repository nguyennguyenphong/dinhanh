"""
Authorization policies for the Tenant bounded context.

Rules:
- Only superusers can create / hard-delete tenants.
- Tenant admins (staff within the tenant) can update their own tenant.
- Feature flags and invitations are managed by tenant admins.
- Audit log is read-only for tenant admins; full access for superusers.
"""
from __future__ import annotations

from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request


class TenantPolicy:
    """
    Stateless policy class — each method either passes silently or raises
    PermissionDenied with a descriptive message.
    """

    @staticmethod
    def can_create(request: Request) -> None:
        """Only superusers (is_staff=True) may create new tenants."""
        if not request.user or not request.user.is_staff:
            raise PermissionDenied("Only staff users can create tenants.")

    @staticmethod
    def can_list(request: Request) -> None:
        """Staff can list all tenants; non-staff users cannot."""
        if not request.user or not request.user.is_staff:
            raise PermissionDenied("Only staff users can list tenants.")

    @staticmethod
    def can_retrieve(request: Request, tenant_id: int) -> None:
        """
        Staff can retrieve any tenant.
        Regular users can only retrieve their own tenant (stored in request.tenant_id
        set by TenantMiddleware).
        """
        if not request.user:
            raise PermissionDenied("Authentication required.")
        if request.user.is_staff:
            return
        user_tenant_id = getattr(request, "tenant_id", None)
        if user_tenant_id != tenant_id:
            raise PermissionDenied("You can only access your own tenant.")

    @staticmethod
    def can_update(request: Request, tenant_id: int) -> None:
        """Staff can update any tenant; tenant admins can update their own."""
        if not request.user:
            raise PermissionDenied("Authentication required.")
        if request.user.is_staff:
            return
        user_tenant_id = getattr(request, "tenant_id", None)
        if user_tenant_id != tenant_id:
            raise PermissionDenied("You can only update your own tenant.")
        # Additionally require is_tenant_admin flag if present
        if not getattr(request.user, "is_tenant_admin", False):
            raise PermissionDenied("Tenant admin role required.")

    @staticmethod
    def can_deactivate(request: Request) -> None:
        """Only staff can deactivate tenants."""
        if not request.user or not request.user.is_staff:
            raise PermissionDenied("Only staff users can deactivate tenants.")

    @staticmethod
    def can_hard_delete(request: Request) -> None:
        """Only superusers (is_superuser=True) can hard-delete tenants."""
        if not request.user or not request.user.is_superuser:
            raise PermissionDenied("Only superusers can permanently delete tenants.")

    @staticmethod
    def can_manage_feature_flags(request: Request, tenant_id: int) -> None:
        if not request.user:
            raise PermissionDenied("Authentication required.")
        if request.user.is_staff:
            return
        user_tenant_id = getattr(request, "tenant_id", None)
        if user_tenant_id != tenant_id:
            raise PermissionDenied("You can only manage feature flags for your own tenant.")
        if not getattr(request.user, "is_tenant_admin", False):
            raise PermissionDenied("Tenant admin role required.")

    @staticmethod
    def can_manage_invitations(request: Request, tenant_id: int) -> None:
        if not request.user:
            raise PermissionDenied("Authentication required.")
        if request.user.is_staff:
            return
        user_tenant_id = getattr(request, "tenant_id", None)
        if user_tenant_id != tenant_id:
            raise PermissionDenied("You can only manage invitations for your own tenant.")
        if not getattr(request.user, "is_tenant_admin", False):
            raise PermissionDenied("Tenant admin role required.")

    @staticmethod
    def can_read_audit_logs(request: Request, tenant_id: int) -> None:
        if not request.user:
            raise PermissionDenied("Authentication required.")
        if request.user.is_staff:
            return
        user_tenant_id = getattr(request, "tenant_id", None)
        if user_tenant_id != tenant_id:
            raise PermissionDenied("You can only view audit logs for your own tenant.")
        if not getattr(request.user, "is_tenant_admin", False):
            raise PermissionDenied("Tenant admin role required.")