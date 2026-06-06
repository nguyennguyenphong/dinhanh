"""
Celery tasks for the Tenant bounded context.

Tasks handle background work:
  - Sending invitation emails
  - Expiring stale invitations
  - Deactivating expired trial/subscription tenants
"""
from __future__ import annotations

import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="tenants.tasks.send_invitation_email",
)
def send_invitation_email(
    self,
    invitation_id: int,
    tenant_name: str,
    email: str,
    token: str,
    expires_at: str,
) -> None:
    """
    Send invitation email to the invited user.
    Retries up to 3 times on failure with 60s back-off.
    """
    try:
        from django.core.mail import send_mail
        from django.conf import settings

        accept_url = f"{settings.FRONTEND_BASE_URL}/invitations/accept/?token={token}"

        send_mail(
            subject=f"You have been invited to join {tenant_name}",
            message=(
                f"You have been invited to join {tenant_name}.\n\n"
                f"Click the link below to accept your invitation:\n{accept_url}\n\n"
                f"This invitation expires on {expires_at}."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        logger.info("Invitation email sent: invitation_id=%s email=%s", invitation_id, email)
    except Exception as exc:
        logger.error(
            "Failed to send invitation email: invitation_id=%s error=%s",
            invitation_id,
            exc,
        )
        raise self.retry(exc=exc)


@shared_task(name="tenants.tasks.expire_stale_invitations")
def expire_stale_invitations() -> dict:
    """
    Periodic task: mark PENDING invitations that have passed their expiry as EXPIRED.
    Schedule with Celery Beat: e.g. every hour.
    """
    from tenants.models import TenantInvitation

    now = timezone.now()
    expired_qs = TenantInvitation.objects.filter(
        status="PENDING",
        expires_at__lt=now,
    )
    count = expired_qs.update(status="EXPIRED")
    logger.info("Expired %d stale invitations.", count)
    return {"expired_count": count}


@shared_task(name="tenants.tasks.deactivate_expired_subscriptions")
def deactivate_expired_subscriptions() -> dict:
    """
    Periodic task: deactivate tenants whose subscription has expired.
    Schedule with Celery Beat: e.g. daily at midnight.
    """
    from tenants.models import Tenant, TenantAuditLog

    now = timezone.now()
    expired_tenants = Tenant.objects.filter(
        is_active=True,
        subscription_expires_at__lt=now,
    ).exclude(plan="ENTERPRISE")

    deactivated_ids = []
    for tenant in expired_tenants:
        tenant.is_active = False
        tenant.save(update_fields=["is_active", "updated_at"])

        TenantAuditLog.objects.create(
            tenant=tenant,
            action="UPDATE",
            module="tenants.tasks",
            object_type="Tenant",
            object_id=str(tenant.pk),
            object_repr=str(tenant),
            old_values={"is_active": True},
            new_values={"is_active": False},
            changes={"is_active": {"old": True, "new": False}},
        )
        deactivated_ids.append(tenant.pk)

    logger.info(
        "Deactivated %d tenants due to expired subscriptions: ids=%s",
        len(deactivated_ids),
        deactivated_ids,
    )
    return {"deactivated_count": len(deactivated_ids), "tenant_ids": deactivated_ids}


@shared_task(name="tenants.tasks.notify_expiring_subscriptions")
def notify_expiring_subscriptions(days_before: int = 7) -> dict:
    """
    Periodic task: notify tenants whose subscription expires within `days_before` days.
    """
    from tenants.models.tenants import Tenant
    from django.core.mail import send_mail
    from django.conf import settings

    now = timezone.now()
    threshold = now + timedelta(days=days_before)

    expiring = Tenant.objects.filter(
        is_active=True,
        subscription_expires_at__range=(now, threshold),
    ).exclude(plan="ENTERPRISE")

    notified = 0
    for tenant in expiring:
        try:
            # In production, fetch contact email from tenant settings or a
            # related TenantContact model.
            contact_email = tenant.settings.get("contact_email")
            if not contact_email:
                continue

            remaining = (tenant.subscription_expires_at - now).days
            send_mail(
                subject=f"Your {tenant.name} subscription expires in {remaining} days",
                message=(
                    f"Hi,\n\nYour subscription for {tenant.name} will expire on "
                    f"{tenant.subscription_expires_at.strftime('%Y-%m-%d')}.\n\n"
                    f"Please renew to avoid service interruption."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[contact_email],
                fail_silently=True,
            )
            notified += 1
        except Exception:
            logger.exception("Failed to notify tenant pk=%s", tenant.pk)

    return {"notified_count": notified}