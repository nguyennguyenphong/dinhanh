from django.db import models
from django.utils.translation import gettext_lazy as _

class FeatureFlagAuditLog(models.Model):
    """
    Audit log for feature flag changes

    Features:
    - Track all flag changes
    - Record who made changes and when
    - Support for compliance audits
    """

    ACTION_CHOICES = (
        ("CREATE", _("Create - Flag created")),
        ("UPDATE", _("Update - Flag modified")),
        ("DELETE", _("Delete - Flag deleted")),
        ("ENABLE", _("Enable - Flag enabled")),
        ("DISABLE", _("Disable - Flag disabled")),
    )

    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="feature_flag_audit_logs",
        db_index=True,
        help_text="Tenant that owns this audit log",
    )

    flag = models.ForeignKey(
        "feature_flags.FeatureFlag",
        on_delete=models.CASCADE,
        related_name="feature_flag_audit_logs",
        help_text="Feature flag affected by this change",
    )

    # ========================================================================
    # ACTION DETAILS
    # ========================================================================

    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        db_index=True,
        help_text="Type of action performed",
    )

    actor = models.ForeignKey(
        "accounts.UserAccount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="feature_flag_actions_performed",
        help_text="User who performed the action",
    )

    # ========================================================================
    # CHANGE DETAILS
    # ========================================================================

    old_values = models.JSONField(null=True, blank=True, help_text="Previous values")
    new_values = models.JSONField(null=True, blank=True, help_text="New values")

    reason = models.TextField(blank=True, null=True, help_text="Reason for the change")

    # ========================================================================
    # TIMESTAMPS
    # ========================================================================

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "feature_flag_audit_logs"
        verbose_name = _("Feature Flag Audit Log")
        verbose_name_plural = _("Feature Flag Audit Logs")
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["tenant", "created_at"], name="idx_feature_audit_tenant_created"
            ),
            models.Index(
                fields=["flag", "created_at"], name="idx_feature_audit_flag_created"
            ),
        ]

    def __str__(self):
        return f"{self.action} - {self.flag.key}"

    @classmethod
    def log_action(
        cls,
        tenant,
        flag,
        action,
        actor=None,
        old_values=None,
        new_values=None,
        reason=None,
    ):
        """
        Log a feature flag action

        Args:
            tenant: Tenant instance
            flag: FeatureFlag instance
            action: Action type
            actor: UserAccount instance
            old_values: Previous values
            new_values: New values
            reason: Reason for action

        Returns:
            FeatureFlagAuditLog instance
        """
        return cls.objects.create(
            tenant=tenant,
            flag=flag,
            action=action,
            actor=actor,
            old_values=old_values,
            new_values=new_values,
            reason=reason,
        )
