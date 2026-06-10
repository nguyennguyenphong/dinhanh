from django.db import models
from django.utils.translation import gettext_lazy as _


class RolePermissionAuditLog(models.Model):
    """
    Audit log for role-permission changes

    Features:
    - Track all role-permission assignments and revocations
    - Record who made changes and when
    - Support for compliance and security audits
    - Immutable audit trail

    Example:
        log = RolePermissionAuditLog.objects.create(
            tenant=tenant,
            role=role,
            permission=permission,
            action='ASSIGN',
            actor_id=admin.id,
            actor_username=admin.username
        )
    """

    ACTION_CHOICES = (
        ("ASSIGN", _("Assign - Permission assigned to role")),
        ("REVOKE", _("Revoke - Permission revoked from role")),
        ("RESTORE", _("Restore - Permission restored to role")),
        ("BATCH_ASSIGN", _("Batch Assign - Multiple permissions assigned")),
        ("BATCH_REVOKE", _("Batch Revoke - Multiple permissions revoked")),
    )

    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="role_permission_audit_logs",
        db_index=True,
        help_text="Tenant that owns this audit log",
    )

    role = models.ForeignKey(
        "Role",
        on_delete=models.CASCADE,
        related_name="permission_audit_logs",
        db_index=True,
        help_text="Role affected by this change",
    )

    permission = models.ForeignKey(
        "Permission",
        on_delete=models.CASCADE,
        related_name="role_audit_logs",
        null=True,
        blank=True,
        help_text="Permission affected (null for batch operations)",
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

    actor_id = models.IntegerField(
        null=True, blank=True, help_text="User ID who performed the action"
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
        default=1, help_text="Number of permissions affected (for batch operations)"
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
        db_table = "role_permission_audit_logs"
        verbose_name = _("Role Permission Audit Log")
        verbose_name_plural = _("Role Permission Audit Logs")
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["tenant", "created_at"],
                name="idx_role_perm_tenant_created",
            ),
            models.Index(
                fields=["role", "created_at"], name="idx_role_perm_at_role_created"
            ),
            models.Index(fields=["action"], name="idx_role_perm_audit_action"),
        ]

    def __str__(self):
        return f"{self.action} - {self.role.slug} - {self.permission.codename if self.permission else 'batch'}"

    @classmethod
    def log_action(
        cls,
        tenant,
        role,
        permission=None,
        action="ASSIGN",
        actor_id=None,
        actor_username=None,
        reason=None,
        affected_count=1,
        ip_address=None,
        user_agent=None,
    ):
        """
        Log a role-permission action

        Args:
            tenant: Tenant instance
            role: Role instance
            permission: Permission instance (optional for batch)
            action: Action type
            actor_id: User ID who performed action
            actor_username: Username who performed action
            reason: Reason for action
            affected_count: Number of permissions affected
            ip_address: IP address of actor
            user_agent: User agent of actor

        Returns:
            RolePermissionAuditLog instance
        """
        return cls.objects.create(
            tenant=tenant,
            role=role,
            permission=permission,
            action=action,
            actor_id=actor_id,
            actor_username=actor_username,
            reason=reason,
            affected_count=affected_count,
            ip_address=ip_address,
            user_agent=user_agent,
        )
