from django.db import models
from django.utils.translation import gettext_lazy as _


class PermissionAuditLog(models.Model):
    """
    Audit log for permission changes

    Features:
    - Track all permission modifications
    - Record who made changes and when
    - Support for compliance and security audits
    """

    ACTION_CHOICES = (
        ("CREATE", _("Create")),
        ("UPDATE", _("Update")),
        ("DELETE", _("Delete")),
        ("ASSIGN", _("Assign")),
        ("REVOKE", _("Revoke")),
    )

    id = models.BigAutoField(primary_key=True)

    # Tenant
    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="permission_audit_logs",
        db_index=True,
    )

    # Permission reference
    permission = models.ForeignKey(
        "accounts.Permission",
        on_delete=models.CASCADE,
        related_name="permission_audit_logs",
        null=True,
        blank=True,
    )

    # Action details
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, db_index=True)
    actor_id = models.IntegerField(
        null=True, blank=True, help_text="User ID who performed the action"
    )
    actor_username = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        help_text="Username who performed the action",
    )

    # Changes
    old_values = models.JSONField(null=True, blank=True, help_text="Previous values")
    new_values = models.JSONField(null=True, blank=True, help_text="New values")

    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "permission_audit_logs"
        verbose_name = _("Permission Audit Log")
        verbose_name_plural = _("Permission Audit Logs")
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["tenant", "created_at"]),
            models.Index(fields=["action"]),
        ]

    def __str__(self):
        return (
            f"{self.action} - {self.permission.codename if self.permission else 'N/A'}"
        )
