# ============================================================================
# FILE: apps/notifications/models.py
# Omnichannel Notification Ledger & Partitioned Dispatch Logs
# ============================================================================

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from safedelete.models import SOFT_DELETE_CASCADE, SafeDeleteModel


class Notification(SafeDeleteModel):
    """
    Notification model tracking outbound communication execution logs and transactional states.

    Features:
    - High-Velocity Queue Ledger: Acts as a buffering database broker queue for background asynchronous worker workers.
    - Polymorphic Recipient Routing: Maps destinations to standard accounts, external passengers, or station employees.
    - Generic Target Referencing: Binds communications loosely onto domain assets (bookings, trips, consignments) via loose indexing.
    - PostgreSQL Range Partitioning: Table structure is physically split into temporal sub-tables by 'created_at' ranges.

    Recipient Types:
    - USER: Standard system infrastructure accounts or internal staff console endpoints.
    - CUSTOMER: B2C passengers or cargo senders/receivers registered inside mobile databases.
    - EMPLOYEE: Active transport operatives, drivers, ticket agents, or station conductors.

    Statuses:
    - PENDING: Staged row awaiting background integration tasks (e.g., Celery, Cron) to claim and transmit to gateways.
    - SENT: Third-party carrier API (Twilio, SendGrid, Zalo Cloud) confirmed receipt and delivery successfully.
    - FAILED: Gateway returned processing anomalies, marked for worker examination or automated retry sweeps.
    - CANCELLED: Suppressed manually by system command blocks before transmission execution occurred.

    Example:
        # Stage an outbound SMS alert notification row for background delivery processing
        alert = Notification.objects.create(
            template_id=42,
            recipient_type='CUSTOMER',
            recipient_id=8901,
            recipient_phone='+84909123456',
            channel='SMS',
            body='Trip HCMC-NhaTrang on 2026-06-01 is preparing for boarding. Please arrive 30m early.',
            ref_type='trip',
            ref_id=5502
        )
    """

    _safedelete_policy = SOFT_DELETE_CASCADE

    RECIPIENT_TYPE_CHOICES = (
        (
            "USER",
            _("User - Generic console accounts or internal admin portal entities"),
        ),
        (
            "CUSTOMER",
            _("Customer - Active consumer passengers or freight logistical clients"),
        ),
        (
            "EMPLOYEE",
            _(
                "Employee - On-field fleet transport operational staff or station managers"
            ),
        ),
    )

    STATUS_CHOICES = (
        (
            "PENDING",
            _(
                "Pending - Staged in transmission queue, awaiting background daemon pickup"
            ),
        ),
        (
            "SENT",
            _("Sent - External telecom/email gateway successfully authorized delivery"),
        ),
        (
            "FAILED",
            _("Failed - Gateway aborted transaction execution, stalled in error state"),
        ),
        (
            "CANCELLED",
            _(
                "Cancelled - Voluntarily terminated by administrative task overrides before dispatch"
            ),
        ),
    )

    # Using BigAutoField matches BIGSERIAL primary key target requirements
    id = models.BigAutoField(primary_key=True)

    # Due to PostgreSQL native partitioning constraints, Django's default AutoField
    # might cause migration conflicts if not explicitly declared alongside partitioning strategies.

    tenant_id = models.IntegerField(
        default=1,  # Matches NOT NULL DEFAULT 1 from requirement
        help_text="Tenant corporate node owning and financing this communications ledger execution instance",
    )

    # ========================================================================
    # RELATIONSHIPS & BLUEPRINT CONNECTIONS
    # ========================================================================

    template = models.ForeignKey(
        "notifications.NotificationTemplate",
        on_delete=models.SET_NULL,  # Matches REFERENCES notification_templates(id) ON DELETE SET NULL
        related_name="notifications",
        null=True,
        blank=True,
        db_index=True,
        help_text="The base blueprint template layer utilized to construct this message payload copy text",
    )

    # ========================================================================
    # POLYMORPHIC RECIPIENT TELEMETRY METADATA
    # ========================================================================

    recipient_type = models.CharField(
        max_length=20,
        choices=RECIPIENT_TYPE_CHOICES,  # Enforces structural comment boundaries
        help_text="The structural category classification governing the target recipient profile mapping layout",
    )

    recipient_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="The abstract primary key referencing the target user/customer/employee table row based on recipient_type",
    )

    recipient_phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,  # Matches VARCHAR(20) nullable parameters
        help_text="Cellular telecommunication string destination required for SMS or ZALO dispatches",
    )

    recipient_email = models.EmailField(
        max_length=254,  # Matches VARCHAR(254) cleanly via standard Django definitions
        null=True,
        blank=True,
        help_text="Electronic digital mail destination address required for EMAIL channel delivery workflows",
    )

    # ========================================================================
    # CONTENT TEXT TRANSLATION COPY BLOCKS
    # ========================================================================

    channel = models.CharField(
        max_length=20,
        help_text="The explicit physical medium selected to route this communication text block (e.g., SMS, EMAIL, PUSH)",
    )

    subject = models.CharField(
        max_length=500,  # Matches VARCHAR(500) nullable parameter specifications
        null=True,
        blank=True,
        help_text="The specific message title or email subject text banner used during transmission delivery packages",
    )

    body = models.TextField(
        help_text="The finalized rendered plaintext or rich HTML text body sent down to third-party telecommunication networks"
    )

    # ========================================================================
    # QUEUE MACHINERY & TRANSMISSION STATE REGISTERS
    # ========================================================================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",  # Matches NOT NULL DEFAULT 'PENDING'
        help_text="The real-time operational processing milestone tracking this transaction through queue worker handlers",
    )

    retry_count = models.SmallIntegerField(
        default=0,  # Matches SMALLINT NOT NULL DEFAULT 0
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Current exponential backoff retry tally tracking delivery attempts made by pipeline workers before failure termination",
    )

    error_msg = models.TextField(
        null=True,
        blank=True,
        help_text="Stashes external vendor diagnostic telemetry dumps or exception logs during failed transmission attempts",
    )

    # ========================================================================
    # LOOSE LOGISTICAL MULTI-DOMAIN LINK REFERENCES
    # ========================================================================

    ref_type = models.CharField(
        max_length=60,
        null=True,
        blank=True,
        help_text="The application string name token mapping target business modules (e.g., booking, trip, consignment)",
    )

    ref_id = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="The corresponding primary key value pointing onto the source domain model indicated by ref_type",
    )

    # ========================================================================
    # CHRONOLOGY LANDMARKS (CRITICAL: PARTITION KEY)
    # ========================================================================

    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timezone-aware timestamp logging exactly when the third-party communication channel confirmed delivery clearance",
    )

    created_at = models.DateTimeField(
        default=models.functions.Now,  # Matches NOT NULL DEFAULT NOW() at native execution compilation
        help_text="Timezone-aware anchor tracking record entry. This is the structural PARTITION KEY routing rows to distinct physical storage sub-tables.",
    )

    class Meta:
        db_table = "notifications"
        verbose_name = _("Omnichannel Notification Log")
        verbose_name_plural = _("Omnichannel Notification Logs")

        # Application-layer ordering matches physical composite status indexes
        ordering = ["status", "-created_at"]

        # ====================================================================
        # COMPOSITE HIGH-PERFORMANCE PRODUCTION INDEXES
        # ====================================================================

        indexes = [
            # Replicates exact structure of: CREATE INDEX idx_notifications_status ON notifications(status, created_at);
            # Critical optimization for Queue Workers querying: Notification.objects.filter(status='PENDING').order_by('created_at')
            models.Index(
                fields=["status", "created_at"], name="idx_notifications_status"
            ),
            # Replicates exact structure of: CREATE INDEX idx_notifications_ref ON notifications(ref_type, ref_id);
            # Critical optimization for finding all alerts linked to a single specific Order Booking or Logistics Parcel
            models.Index(fields=["ref_type", "ref_id"], name="idx_notifications_ref"),
        ]

        constraints = [
            # Direct database-level CHECK constraint enforcing execution state taxonomy compliance
            models.CheckConstraint(
                condition=models.Q(
                    status__in=["PENDING", "SENT", "FAILED", "CANCELLED"]
                ),
                name="chk_notification_status_rules",
            ),
            # Direct database-level CHECK constraint restricting recipient classification parameters
            models.CheckConstraint(
                condition=models.Q(recipient_type__in=["USER", "CUSTOMER", "EMPLOYEE"]),
                name="chk_notification_recipient_type_enum",
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"Notification #{self.id} [{self.channel}] -> {self.recipient_type} (Status: {self.status})"

    # ========================================================================
    # PRODUCTION COMPLIANCE & ASYNCHRONOUS WORKER QUEUE INTERFACES
    # ========================================================================

    def clean(self):
        """
        Application-layer schema alignment checks validating parameter mappings before queuing tasks.
        """
        super().clean()

        # Routing safety rule: Verify destination parameters exist based on selected transmission channels
        if self.channel == "EMAIL" and not self.recipient_email:
            raise ValidationError(
                {
                    "recipient_email": _(
                        "Routing Error: EMAIL channel dispatches require a filled destination recipient_email field."
                    )
                }
            )

        if self.channel in ["SMS", "ZALO"] and not self.recipient_phone:
            raise ValidationError(
                {
                    "recipient_phone": _(
                        "Routing Error: Telecommunication channels (SMS/ZALO) require a filled recipient_phone field."
                    )
                }
            )

    def mark_as_transmitted(self):
        """
        Locks the message log status into successfully dispatched state.
        Executed by asynchronous workers after third-party networks clear API transmission blocks.
        """
        from django.utils import timezone

        self.status = "SENT"
        self.sent_at = timezone.now()
        self.error_msg = None
        self.save(update_fields=["status", "sent_at", "error_msg"])

    def mark_as_failed(self, error_exception_text):
        """
        Tracks and manages transmission interruptions. Triggers automated queue recalculation thresholds.

        Args:
            error_exception_text: String diagnostic traceback payload returned from network API gateways.
        """
        self.error_msg = error_exception_text

        # Exponential Backoff Retry Check: evaluate if the record can safely stay in queue rotation
        if self.retry_count < 3:
            self.status = "PENDING"  # Leave staged inside worker retrieval nets for another sweep iteration
            self.retry_count += 1
        else:
            self.status = "FAILED"  # Hard-cap exhausted, move row out of background queue scanning pipelines

        self.save(update_fields=["status", "retry_count", "error_msg"])
