from django.db import models
from django.utils.translation import gettext_lazy as _

from tenants.models.tenants import Tenant
from .branches import Branch


class BranchAuditLog(models.Model):
    """
    Audit log for branch changes

    Features:
    - Track branch creation, updates, and deletions
    - Record who made changes and when
    - Support for compliance audits
    """

    ACTION_CHOICES = (
        ("CREATE", _("Create - Branch created")),
        ("UPDATE", _("Update - Branch modified")),
        ("DELETE", _("Delete - Branch deleted")),
        ("ACTIVATE", _("Activate - Branch activated")),
        ("DEACTIVATE", _("Deactivate - Branch deactivated")),
    )

    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="branch_audit_logs",
        db_index=True,
        help_text="Tenant that owns this audit log",
    )

    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name="branch_audit_logs",
        null=True,
        blank=True,
        help_text="Branch affected by this change",
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
        related_name="branch_actions_performed",
        help_text="User who performed the action",
    )
    actor_username = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        help_text="Username who performed the action",
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
        db_table = "branch_audit_logs"
        verbose_name = _("Branch Audit Log")
        verbose_name_plural = _("Branch Audit Logs")
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["tenant", "created_at"], name="idx_branch_audit_tenant_created"
            ),
            models.Index(
                fields=["branch", "created_at"], name="idx_branch_audit_branch_created"
            ),
        ]

    def __str__(self):
        return f"{self.action} - {self.branch.code if self.branch else 'N/A'}"

    @classmethod
    def log_action(
        cls,
        tenant,
        branch,
        action,
        actor=None,
        actor_username=None,
        old_values=None,
        new_values=None,
        reason=None,
    ):
        """
        Log a branch action

        Args:
            tenant: Tenant instance
            branch: Branch instance
            action: Action type
            actor: UserAccount instance
            actor_username: Username
            old_values: Previous values
            new_values: New values
            reason: Reason for action

        Returns:
            BranchAuditLog instance
        """
        return cls.objects.create(
            tenant=tenant,
            branch=branch,
            action=action,
            actor=actor,
            actor_username=actor_username,
            old_values=old_values,
            new_values=new_values,
            reason=reason,
        )
