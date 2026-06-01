from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRoleAuditLog(models.Model):
    """
    Audit log for user-role changes

    Features:
    - Track all user-role assignments and revocations
    - Record who made changes and when
    - Support for compliance and security audits
    - Immutable audit trail

    Example:
        log = UserRoleAuditLog.objects.create(
            tenant=tenant,
            user=user,
            role=role,
            action='ASSIGN',
            actor=admin_user,
            actor_username=admin_user.username
        )
    """

    ACTION_CHOICES = (
        ("ASSIGN", _("Assign - Role assigned to user")),
        ("REVOKE", _("Revoke - Role revoked from user")),
        ("RESTORE", _("Restore - Role restored to user")),
        ("BATCH_ASSIGN", _("Batch Assign - Multiple roles assigned")),
        ("BATCH_REVOKE", _("Batch Revoke - Multiple roles revoked")),
        ("EXPIRE", _("Expire - Role assignment expired")),
    )

    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="user_role_audit_logs",
        db_index=True,
        help_text="Tenant that owns this audit log",
    )

    user = models.ForeignKey(
        "UserAccount",
        on_delete=models.CASCADE,
        related_name="role_audit_logs",
        db_index=True,
        help_text="User affected by this change",
    )

    role = models.ForeignKey(
        "Role",
        on_delete=models.CASCADE,
        related_name="user_audit_logs",
        null=True,
        blank=True,
        help_text="Role affected (null for batch operations)",
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
        "UserAccount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="role_actions_performed",
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

    reason = models.TextField(blank=True, null=True, help_text="Reason for the change")

    affected_count = models.IntegerField(
        default=1, help_text="Number of roles affected (for batch operations)"
    )

    # ========================================================================
    # METADATA
    # ========================================================================

    ip_address = models.GenericIPAddressField(
        null=True, blank=True, help_text="IP address of the actor"
    )
    user_agent = models.TextField(
        null=True, blank=True, help_text="User agent of the actor"
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "user_role_audit_logs"
        verbose_name = _("User Role Audit Log")
        verbose_name_plural = _("User Role Audit Logs")
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["tenant", "created_at"],
                name="idx_user_role_tenant_created",
            ),
            models.Index(
                fields=["user", "created_at"], name="idx_user_role_at_user_created"
            ),
            models.Index(fields=["action"], name="idx_user_role_audit_action"),
        ]

    def __str__(self):
        return f"{self.action} - {self.user.username} - {self.role.slug if self.role else 'batch'}"

    @classmethod
    def log_action(
        cls,
        tenant,
        user,
        role=None,
        action="ASSIGN",
        actor=None,
        actor_username=None,
        reason=None,
        affected_count=1,
        ip_address=None,
        user_agent=None,
    ):
        """
        Log a user-role action

        Args:
            tenant: Tenant instance
            user: UserAccount instance
            role: Role instance (optional for batch)
            action: Action type
            actor: UserAccount instance who performed action
            actor_username: Username who performed action
            reason: Reason for action
            affected_count: Number of roles affected
            ip_address: IP address of actor
            user_agent: User agent of actor

        Returns:
            UserRoleAuditLog instance
        """
        return cls.objects.create(
            tenant=tenant,
            user=user,
            role=role,
            action=action,
            actor=actor,
            actor_username=actor_username,
            reason=reason,
            affected_count=affected_count,
            ip_address=ip_address,
            user_agent=user_agent,
        )
