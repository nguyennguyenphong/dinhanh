from django.db import models
from django.utils.translation import gettext_lazy as _


class APITokenAuditLog(models.Model):
    """
    Audit log for API token access

    Features:
    - Track all API requests made with tokens
    - Record request details (method, endpoint, status)
    - Track rate limit violations
    - Security monitoring
    """

    ACTION_CHOICES = (
        ("CREATE", _("Create - Token created")),
        ("REVOKE", _("Revoke - Token revoked")),
        ("ACCESS", _("Access - Token used for API request")),
        ("RATE_LIMIT", _("Rate Limit - Rate limit exceeded")),
        ("SCOPE_DENIED", _("Scope Denied - Insufficient scope")),
    )

    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="api_token_audit_logs",
        db_index=True,
        help_text="Tenant that owns this audit log",
    )

    token = models.ForeignKey(
        "api_tokens.APIToken",
        on_delete=models.CASCADE,
        related_name="api_token_audit_logs",
        help_text="API token used",
    )

    # ========================================================================
    # REQUEST DETAILS
    # ========================================================================

    action = models.CharField(
        max_length=20, choices=ACTION_CHOICES, db_index=True, help_text="Type of action"
    )

    method = models.CharField(
        max_length=10, null=True, blank=True, help_text="HTTP method (GET, POST, etc.)"
    )

    endpoint = models.CharField(
        max_length=255, null=True, blank=True, help_text="API endpoint accessed"
    )

    status_code = models.IntegerField(
        null=True, blank=True, help_text="HTTP response status code"
    )

    ip_address = models.GenericIPAddressField(
        null=True, blank=True, help_text="IP address of request"
    )

    user_agent = models.TextField(
        blank=True, null=True, help_text="User agent of request"
    )

    # ========================================================================
    # TIMESTAMPS
    # ========================================================================

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "api_token_audit_logs"
        verbose_name = _("API Token Audit Log")
        verbose_name_plural = _("API Token Audit Logs")
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["token", "created_at"], name="idx_api_audit_token_created"
            ),
            models.Index(fields=["action"], name="idx_api_audit_action"),
        ]

    def __str__(self):
        return f"{self.action} - {self.token.name}"

    @classmethod
    def log_action(
        cls,
        tenant,
        token,
        action,
        method=None,
        endpoint=None,
        status_code=None,
        ip_address=None,
        user_agent=None,
    ):
        """
        Log an API token action

        Args:
            tenant: Tenant instance
            token: APIToken instance
            action: Action type
            method: HTTP method
            endpoint: API endpoint
            status_code: HTTP status code
            ip_address: IP address
            user_agent: User agent

        Returns:
            APITokenAuditLog instance
        """
        return cls.objects.create(
            tenant=tenant,
            token=token,
            action=action,
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            ip_address=ip_address,
            user_agent=user_agent,
        )
