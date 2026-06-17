from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class SystemConfigAuditLog(BaseModel):
    ACTION_CHOICES = (
        ("CREATE", _("Create - Config created")),
        ("UPDATE", _("Update - Config modified")),
        ("DELETE", _("Delete - Config deleted")),
    )

    id = models.BigAutoField(primary_key=True)
    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="config_audit_logs",
        db_index=True,
    )
    config = models.ForeignKey(
        "system_config.SystemConfig",
        on_delete=models.CASCADE,
        related_name="system_config_audit_logs",
        null=True,
        blank=True,
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, db_index=True)
    actor = models.ForeignKey(
        "accounts.UserAccount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="config_actions_performed",
    )
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    reason = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "system_config_audit_logs"
        verbose_name = _("System Config Audit Log")
        verbose_name_plural = _("System Config Audit Logs")
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["tenant", "created_at"], name="idx_conf_at_tenant_created"
            ),
            models.Index(
                fields=["config", "created_at"], name="idx_audit_config_created"
            ),
        ]

    def __str__(self):
        return f"{self.action} - {self.config.key if self.config else 'N/A'}"
