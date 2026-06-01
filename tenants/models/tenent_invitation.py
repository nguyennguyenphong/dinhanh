from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from tenants.models.tenants import Tenant


class TenantInvitation(models.Model):
    """
    Undangan untuk user tham gia tenant
    """

    STATUS_CHOICES = (
        ("PENDING", _("Pending")),
        ("ACCEPTED", _("Accepted")),
        ("REJECTED", _("Rejected")),
        ("EXPIRED", _("Expired")),
    )

    id = models.AutoField(primary_key=True)
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="invitations"
    )
    email = models.EmailField()
    token = models.CharField(max_length=255, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    invited_by_id = models.IntegerField()

    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tenant_invitations"
        verbose_name = _("Tenant Invitation")
        verbose_name_plural = _("Tenant Invitations")

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.tenant.code} - {self.email}"
