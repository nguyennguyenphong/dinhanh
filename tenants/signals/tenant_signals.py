# ============================================================================
# FILE: tenants/signals/tenant_signals.py
# ============================================================================
from django.db.models.signals import post_save
from django.dispatch import receiver
from tenants.models.tenants import Tenant
import logging

logger = logging.getLogger("audit_trail")

@receiver(post_save, sender=Tenant)
def handle_tenant_post_save(sender, instance, created, **kwargs):
    """
    System hook evaluating state changes for critical audit indexing.
    """
    if created:
        logger.info(f"[AUDIT] New tenant infrastructure built: {instance.code} using Currency: {instance.currency}")
    else:
        logger.info(f"[AUDIT] Tenant modified: {instance.code} Status change to Active={instance.is_active}")