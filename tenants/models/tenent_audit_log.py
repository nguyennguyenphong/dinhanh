from django.db import models
from django.utils.translation import gettext_lazy as _


class TenantAuditLog(models.Model):
    """
    Audit log cho mỗi tenant
    Ghi lại tất cả thay đổi dữ liệu
    """

    ACTION_CHOICES = (
        ("CREATE", _("Create")),
        ("UPDATE", _("Update")),
        ("DELETE", _("Delete")),
        ("LOGIN", _("Login")),
        ("EXPORT", _("Export")),
    )

    id = models.BigAutoField(primary_key=True)
    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="tenant_audit_logs",
        db_index=True,
    )
    user_id = models.IntegerField(null=True, blank=True)
    username = models.CharField(max_length=150, null=True, blank=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, db_index=True)
    module = models.CharField(max_length=100, db_index=True)
    object_type = models.CharField(max_length=100, null=True, blank=True)
    object_id = models.CharField(max_length=50, null=True, blank=True)
    object_repr = models.TextField(null=True, blank=True)

    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    changes = models.JSONField(null=True, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        default="SUCCESS",
        choices=[("SUCCESS", "Success"), ("FAILED", "Failed")],
    )
    error_message = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "tenant_audit_logs"
        verbose_name = _("Tenant Audit Log")
        verbose_name_plural = _("Tenant Audit Logs")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tenant", "created_at"]),
            models.Index(fields=["module", "action"]),
        ]

    def __str__(self):
        return f"{self.tenant.code} - {self.action} - {self.module}"
