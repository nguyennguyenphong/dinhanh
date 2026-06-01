from django.db import models
from django.utils.translation import gettext_lazy as _


class MenuItemRoleAuditLog(models.Model):
    """
    Audit log for menu item role assignments

    Features:
    - Track role assignments and revocations
    - Record who made changes and when
    - Support for compliance audits
    """

    ACTION_CHOICES = (
        ("ASSIGN", _("Assign - Role assigned to menu item")),
        ("REVOKE", _("Revoke - Role revoked from menu item")),
        ("BATCH_ASSIGN", _("Batch Assign - Multiple roles assigned")),
        ("BATCH_REVOKE", _("Batch Revoke - Multiple roles revoked")),
    )

    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="menu_item_role_audit_logs",
        db_index=True,
        help_text="Tenant that owns this audit log",
    )

    menu_item = models.ForeignKey(
        "MenuItem",
        on_delete=models.CASCADE,
        related_name="role_audit_logs",
        db_index=True,
        help_text="Menu item affected by this change",
    )

    role = models.ForeignKey(
        "accounts.Role",
        on_delete=models.CASCADE,
        related_name="menu_item_audit_logs",
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
        "accounts.UserAccount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="menu_item_role_actions_performed",
        help_text="User who performed the action",
    )
    actor_username = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        help_text="Username who performed the action",
    )

    # ========================================================================
    # DETAILS
    # ========================================================================

    affected_count = models.IntegerField(
        default=1, help_text="Number of roles affected (for batch operations)"
    )

    reason = models.TextField(blank=True, null=True, help_text="Reason for the change")

    # ========================================================================
    # TIMESTAMPS
    # ========================================================================

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "menu_item_role_audit_logs"
        verbose_name = _("Menu Item Role Audit Log")
        verbose_name_plural = _("Menu Item Role Audit Logs")
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["tenant", "created_at"],
                name="idx_menui_role_tenant_created",
            ),
            models.Index(
                fields=["menu_item", "created_at"],
                name="idx_menu_item_role_created",
            ),
            models.Index(fields=["action"], name="idx_menu_item_role_at_action"),
        ]

    def __str__(self):
        return f"{self.action} - {self.menu_item.label}"

    @classmethod
    def log_action(
        cls,
        tenant,
        menu_item,
        role=None,
        action="ASSIGN",
        actor=None,
        actor_username=None,
        affected_count=1,
        reason=None,
    ):
        """
        Log a menu item role action

        Args:
            tenant: Tenant instance
            menu_item: MenuItem instance
            role: Role instance (optional for batch)
            action: Action type
            actor: UserAccount instance
            actor_username: Username
            affected_count: Number of roles affected
            reason: Reason for action

        Returns:
            MenuItemRoleAuditLog instance
        """
        return cls.objects.create(
            tenant=tenant,
            menu_item=menu_item,
            role=role,
            action=action,
            actor=actor,
            actor_username=actor_username,
            affected_count=affected_count,
            reason=reason,
        )
