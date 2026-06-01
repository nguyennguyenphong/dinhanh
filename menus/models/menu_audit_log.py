from django.db import models
from django.utils.translation import gettext_lazy as _


class MenuAuditLog(models.Model):
    """
    Audit log for menu changes
    """

    ACTION_CHOICES = (
        ("CREATE", _("Create - Menu item created")),
        ("UPDATE", _("Update - Menu item modified")),
        ("DELETE", _("Delete - Menu item deleted")),
        ("REORDER", _("Reorder - Menu items reordered")),
    )

    id = models.BigAutoField(primary_key=True)

    tenant = models.ForeignKey(
        "tenants.Tenant", on_delete=models.CASCADE, related_name="menu_audit_logs", db_index=True
    )

    action = models.CharField(max_length=20, choices=ACTION_CHOICES, db_index=True)

    actor = models.ForeignKey(
        "accounts.UserAccount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="menu_actions_performed",
    )

    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "menu_audit_logs"
        verbose_name = _("Menu Audit Log")
        verbose_name_plural = _("Menu Audit Logs")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} - {self.created_at}"
