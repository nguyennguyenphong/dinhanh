from django.db import models
from django.utils.translation import gettext_lazy as _


class TenantFeatureFlag(models.Model):
    """
    Feature flags per tenant
    Bật/tắt tính năng cho từng tenant
    """

    tenant = models.ForeignKey(
        "tenants.Tenant", on_delete=models.CASCADE, related_name="tenant_feature_flags"
    )
    code = models.CharField(
        max_length=100, db_index=True, help_text="Mã feature (VD: ADVANCED_REPORTING)"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    is_enabled = models.BooleanField(default=False)
    rollout_percentage = models.PositiveIntegerField(
        default=100,
        validators=[lambda x: x >= 0 and x <= 100],
        help_text="Phần trăm rollout (0-100)",
    )
    config = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tenant_feature_flags"
        unique_together = ("tenant", "code")
        verbose_name = _("Tenant Feature Flag")
        verbose_name_plural = _("Tenant Feature Flags")

    def __str__(self):
        return f"{self.tenant.code} - {self.code}"
