from django.db import models
from django.utils.translation import gettext_lazy as _


class AuditLogArchive(models.Model):
    """
    Archive model for old audit logs

    Features:
    - Store archived audit logs separately
    - Reduce main table size
    - Enable long-term retention
    - Support for compliance requirements
    """

    id = models.BigAutoField(primary_key=True)

    # Store original audit log data as JSON
    audit_data = models.JSONField(help_text="Complete audit log data")

    # Original audit log ID
    original_id = models.BigIntegerField(unique=True, help_text="Original audit log ID")

    # Archival information
    archived_at = models.DateTimeField(
        auto_now_add=True, help_text="When this log was archived"
    )
    archived_by_id = models.IntegerField(
        null=True, blank=True, help_text="User who archived this log"
    )

    class Meta:
        db_table = "audit_logs_archive"
        verbose_name = _("Audit Log Archive")
        verbose_name_plural = _("Audit Log Archives")
        ordering = ["-archived_at"]

    def __str__(self):
        return f"Archive - {self.original_id}"
