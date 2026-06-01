
from django.db import models
from django.utils.translation import gettext_lazy as _


class SessionAuditLog(models.Model):
    """
    Audit log for session events

    Features:
    - Track session creation, revocation, and suspicious activity
    - Record IP changes
    - Detect concurrent sessions from different locations
    - Support for security investigations

    Example:
        log = SessionAuditLog.objects.create(
            user=user,
            session=session,
            event_type='LOGIN',
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0...'
        )
    """

    EVENT_CHOICES = (
        ("LOGIN", _("Login - Session created")),
        ("LOGOUT", _("Logout - Session revoked")),
        ("TOKEN_REFRESH", _("Token Refresh - New tokens generated")),
        ("ACTIVITY", _("Activity - Session activity recorded")),
        ("SUSPICIOUS", _("Suspicious - Suspicious activity detected")),
        ("EXPIRED", _("Expired - Session expired")),
        ("REVOKED", _("Revoked - Session revoked for security")),
    )

    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    user = models.ForeignKey(
        "UserAccount",
        on_delete=models.CASCADE,
        related_name="session_audit_logs",
        db_index=True,
        help_text="User who owns the session",
    )
    session = models.ForeignKey(
        "accounts.UserSession",
        on_delete=models.CASCADE,
        related_name="user_session_audit_logs",
        null=True,
        blank=True,
        help_text="Session related to this event",
    )

    # ========================================================================
    # EVENT DETAILS
    # ========================================================================

    event_type = models.CharField(
        max_length=20,
        choices=EVENT_CHOICES,
        db_index=True,
        help_text="Type of session event",
    )
    ip_address = models.GenericIPAddressField(help_text="IP address of the event")
    user_agent = models.TextField(help_text="User agent at time of event")

    # ========================================================================
    # DETAILS
    # ========================================================================

    details = models.JSONField(
        default=dict, blank=True, help_text="Additional event details"
    )

    # ========================================================================
    # TIMESTAMPS
    # ========================================================================

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "session_audit_logs"
        verbose_name = _("Session Audit Log")
        verbose_name_plural = _("Session Audit Logs")
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["user", "created_at"], name="idx_session_audit_user_created"
            ),
            models.Index(fields=["event_type"], name="idx_session_audit_event_type"),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_event_type_display()}"

    @classmethod
    def log_event(cls, user, session, event_type, ip_address, user_agent, details=None):
        """
        Log session event

        Args:
            user: UserAccount instance
            session: UserSession instance (optional)
            event_type: Type of event
            ip_address: IP address
            user_agent: User agent string
            details: Additional details

        Returns:
            SessionAuditLog instance
        """
        return cls.objects.create(
            user=user,
            session=session,
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {},
        )
