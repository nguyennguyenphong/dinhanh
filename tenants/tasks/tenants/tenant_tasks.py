import logging
from celery import shared_task
from tenants.models.tenants import Tenant

logger = logging.getLogger(__name__)

@shared_task(name="tenants.tasks.tenant.initialize_tenant_provisioning_task", max_retries=3)
def initialize_tenant_provisioning_task(tenant_id: int):
    """
    Background worker initializing defaults for new enterprise accounts 
    (such as default feature flags, seed metrics, reports templates structure setup).
    """
    try:
        tenant = Tenant.objects.get(pk=tenant_id)
        logger.info(f"Asynchronously seeding data templates for Tenant: {tenant.name}")
        
        # Scenario: Pre-populating default system infrastructure variables flags
        from tenants.models.tenent_feature_flag import TenantFeatureFlag
        TenantFeatureFlag.objects.get_or_create(
            tenant=tenant,
            code="BASIC_REPORTING",
            defaults={"name": "Basic Reporting Modules", "is_enabled": True}
        )
        return f"Tenant {tenant_id} fully initialized successfully."
    except Tenant.DoesNotExist:
        logger.error(f"Failed to find target Tenant initialization id: {tenant_id}")
        return False