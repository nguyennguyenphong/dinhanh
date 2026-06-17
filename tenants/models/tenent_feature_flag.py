from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


def validate_percentage(value):
    if value < 0 or value > 100:
        raise ValidationError(
            _("%(value)s không phải là phần trăm hợp lệ (0-100)"),
            params={"value": value},
        )


class TenantFeatureFlag(BaseModel):
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
        validators=[validate_percentage],
        help_text="Phần trăm rollout (0-100)",
    )
    config = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "tenant_feature_flags"
        unique_together = ("tenant", "code")
        verbose_name = _("Tenant Feature Flag")
        verbose_name_plural = _("Tenant Feature Flags")

    def __str__(self):
        return f"{self.tenant.code} - {self.code}"
