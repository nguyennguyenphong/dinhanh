import logging

from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(pre_save, sender="branches.Branch")
def branch_pre_save(sender, instance, **kwargs):
    """Capture old state before save so we can compute a diff."""
    if instance.pk:
        try:
            instance._pre_save_state = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._pre_save_state = None
    else:
        instance._pre_save_state = None


@receiver(post_save, sender="branches.Branch")
def branch_post_save(sender, instance, created, **kwargs):
    """Write an ORM-level audit entry for Branch saves not handled by use-cases."""
    from branches.models.branch_audit_log import BranchAuditLog

    action = "CREATE" if created else "UPDATE"
    old_state = getattr(instance, "_pre_save_state", None)

    old_values = None
    new_values = None

    tracked_fields = [
        "code",
        "name",
        "address",
        "phone",
        "email",
        "manager_id",
        "latitude",
        "longitude",
        "timezone",
        "is_active",
    ]

    def serialize_val(val):
        if val is None:
            return None
        return str(val)

    if not created and old_state:
        old_values = {
            f: serialize_val(getattr(old_state, f, None)) for f in tracked_fields
        }
        new_values = {
            f: serialize_val(getattr(instance, f, None)) for f in tracked_fields
        }
        changes = {
            k: {"old": old_values[k], "new": new_values[k]}
            for k in tracked_fields
            if old_values[k] != new_values[k]
        }
        if not changes:
            return
    else:
        new_values = {
            f: serialize_val(getattr(instance, f, None)) for f in tracked_fields
        }

    try:
        BranchAuditLog.objects.create(
            tenant_id=instance.tenant_id,
            branch=instance,
            action=action,
            old_values=old_values,
            new_values=new_values,
            reason="ORM Signal Auto-Audit",
        )
    except Exception:
        logger.exception(
            "Failed to write audit log via signal for Branch pk=%s", instance.pk
        )


@receiver(post_delete, sender="branches.Branch")
def branch_post_delete(sender, instance, **kwargs):
    logger.warning(
        "Branch hard-deleted via ORM: pk=%s code=%s.",
        instance.pk,
        instance.code,
    )
