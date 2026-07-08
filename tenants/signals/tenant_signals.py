"""
Django signals for the Tenant bounded context.

Signals provide a safety-net audit layer at the ORM level.
Primary audit logging happens in use-cases; signals catch any direct
ORM operations that bypass the service layer (e.g. Django admin, shell).
"""

from __future__ import annotations

import logging

from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Tenant signals                                                               #
# --------------------------------------------------------------------------- #


@receiver(pre_save, sender="tenants.Tenant")
def tenant_pre_save(sender, instance, **kwargs):
    """Capture old state before save so we can compute a diff."""
    if instance.pk:
        try:
            instance._pre_save_state = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._pre_save_state = None
    else:
        instance._pre_save_state = None


@receiver(post_save, sender="tenants.Tenant")
def tenant_post_save(sender, instance, created, **kwargs):
    """Write an ORM-level audit entry for Tenant saves not handled by use-cases."""
    from tenants.models.tenant_audit_log import TenantAuditLog

    action = "CREATE" if created else "UPDATE"
    old_state = getattr(instance, "_pre_save_state", None)

    old_values = None
    new_values = None
    changes = None

    if not created and old_state:
        tracked_fields = [
            "name",
            "plan",
            "is_active",
            "currency",
            "default_language",
            "timezone",
            "max_users",
            "max_branches",
            "max_vehicles",
            "subscription_expires_at",
        ]
        old_values = {f: str(getattr(old_state, f, None)) for f in tracked_fields}
        new_values = {f: str(getattr(instance, f, None)) for f in tracked_fields}
        changes = {
            k: {"old": old_values[k], "new": new_values[k]}
            for k in tracked_fields
            if old_values[k] != new_values[k]
        }
        if not changes:
            # Nothing changed - skip writing a noisy audit entry
            return

    try:
        TenantAuditLog.objects.create(
            tenant=instance,
            action=action,
            module="tenants.signals",
            object_type="Tenant",
            object_id=str(instance.pk),
            object_repr=str(instance),
            old_values=old_values,
            new_values=new_values,
            changes=changes,
        )
    except Exception:
        logger.exception(
            "Failed to write audit log via signal for Tenant pk=%s", instance.pk
        )


@receiver(post_delete, sender="tenants.Tenant")
def tenant_post_delete(sender, instance, **kwargs):
    """Log hard-delete events (these bypass use-case audit, so signals catch them)."""
    logger.warning(
        "Tenant hard-deleted via ORM: pk=%s code=%s. " "Audit log FK will be orphaned.",
        instance.pk,
        instance.code,
    )


# --------------------------------------------------------------------------- #
# TenantInvitation signals                                                     #
# --------------------------------------------------------------------------- #


@receiver(post_save, sender="tenants.TenantInvitation")
def invitation_status_changed(sender, instance, created, **kwargs):
    """Log invitation acceptance/expiry for observability."""
    if not created and instance.status in ("ACCEPTED", "EXPIRED", "REJECTED"):
        logger.info(
            "Invitation status changed: tenant=%s email=%s status=%s",
            instance.tenant_id,
            instance.email,
            instance.status,
        )
