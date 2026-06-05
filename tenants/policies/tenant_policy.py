# ============================================================================
# FILE: apps/tenants/policies/tenant_policy.py
# ============================================================================
from rest_framework.exceptions import PermissionDenied

class TenantCreationPolicy:
    """
    Encapsulates enterprise authorization and validation rules prior to execution.
    """
    @staticmethod
    def is_allowed_to_create(user) -> bool:
        """
        Check if the current requesting user has global infrastructure rights.
        Only superusers or explicit SaaS platform administrators can provision tenants.
        """
        if not user or not user.is_authenticated:
            raise PermissionDenied("Authentication credentials were not provided.")
            
        if not user.is_superuser and not getattr(user, "is_platform_admin", False):
            raise PermissionDenied("You do not have administrative privileges to provision a new company.")
            
        return True