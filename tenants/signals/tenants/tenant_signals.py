import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from tenants.models.tenants import Tenant
from tenants.tasks.tenants.tenant_tasks import initialize_tenant_provisioning_task

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Tenant)
def handle_tenant_provisioning(sender, instance, created, **kwargs):
    """
    Triggers asynchronous enterprise pipeline jobs upon successful database commit.
    E.g. Provisioning isolated logical schemas, seeding standard values.
    """
    if created:
        logger.info(f"[Signal] Initializing core tasks for new Tenant: {instance.code}")
        # Call Celery task asynchronously
        initialize_tenant_provisioning_task.delay(instance.id)