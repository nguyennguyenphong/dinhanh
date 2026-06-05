from tenants.models.tenants import Tenant


class TenantPolicy:
    """
    Handles granular enterprise rules on tenant objects.
    Ensures Superadmins or assigned operators perform CRUD actions.
    """

    @staticmethod
    def can_list(user) -> bool:
        return user.is_authenticated and (user.is_superuser or getattr(user, 'is_staff', False))

    @staticmethod
    def can_create(user) -> bool:
        return user.is_authenticated and user.is_superuser

    @staticmethod
    def can_update(user, tenant: Tenant) -> bool:
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        # Enterprise check: context tenant user belongs to
        return getattr(user, 'tenant_id', None) == tenant.id

    @staticmethod
    def can_delete(user, tenant: Tenant) -> bool:
        # Strict rule: Only Global Superadmin can purge data structures
        return user.is_authenticated and user.is_superuser