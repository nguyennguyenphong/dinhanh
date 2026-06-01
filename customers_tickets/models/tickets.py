# ============================================================================
# FILE: apps/bookings/models.py
# Passenger Ticket Item Management Models
# ============================================================================

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from accounts.models.user_accounts import UserAccount  # Custom user model

# Assuming these models exist in your production architecture
from customers_tickets.models.ticket_bookings import TicketBooking
from vehicles.models.seats import Seat


class Ticket(models.Model):
    """
    Ticket model representing an individual passenger boarding pass item.

    Features:
    - Order Composition: Mapped under a parent transactional TicketBooking sheet via CASCADE link
    - Seat Allocation Snapshot: Captures both raw foreign keys and redundant 'seat_code' fields for auditing
    - High-Precision Ledger: Enforces financial safety parameters via strict Decimal types
    - Unique Cryptographic Tokens: Controls distinct QR and barcode indexes used for physical boarding gates
    - Boarding Verification: Tracks gate-house validation metadata (checked_in_by, checked_in_at)

    Passenger Types:
    - ADULT: Standard age passenger profile (Default base tariff rate applied)
    - CHILD: Concessionary minor passenger bracket
    - INFANT: Toddler/lap child specification, usually zero or minimal fixed surcharge fare
    - STUDENT: Subsidized student credential tier specification
    - SENIOR: Subsidized elderly citizen credential tier specification

    Statuses:
    - ACTIVE: Valid boarding pass, open for check-in gates, inventory locked
    - USED: Successfully checked-in and boarded the vehicle at the terminal platform
    - CANCELLED: Aborted prior to dispatch, seat released back to general allocation pool
    - REFUNDED: Voided with complete or partial financial cash reversal logged
    - EXCHANGED: Replaced or re-routed to an alternative seat allocation slot or different trip node
    - EXPIRED: Trip departed, pass unused and voided without check-in clearance logs

    Example:
        # Create an individual active passenger seat ticket
        ticket = Ticket.objects.create(
            booking_id=1052,
            seat_id=45,
            seat_code='A05',
            passenger_name='Tran Van B',
            passenger_type='ADULT',
            base_price=350000.00,
            discount_amount=0.00,
            final_price=350000.00,
            qr_code='TOKEN-QR-HAN-2026-9912X',
            status='ACTIVE'
        )
    """

    PASSENGER_TYPE_CHOICES = (
        ("ADULT", _("Adult - Standard age passenger pricing rate")),
        ("CHILD", _("Child - Concessionary minor age pricing rate")),
        ("INFANT", _("Infant - Toddler or lap child allocation")),
        ("STUDENT", _("Student - Subsidized educational qualification tier")),
        ("SENIOR", _("Senior - Subsidized elderly citizen tier")),
    )

    STATUS_CHOICES = (
        ("ACTIVE", _("Active - Valid ticket, open for terminal boarding gates")),
        ("USED", _("Used - Boarding complete, passenger inside vehicle")),
        ("CANCELLED", _("Cancelled - Aborted ticket, seat returned to pool")),
        (
            "REFUNDED",
            _("Refunded - Terminated with processed banking financial reversal"),
        ),
        (
            "EXCHANGED",
            _("Exchanged - Voided due to seat/trip reassignment modification"),
        ),
        ("EXPIRED", _("Expired - Journey departed, passenger missed check-in window")),
    )

    # Using BigAutoField matches BIGSERIAL primary key target requirements
    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    booking = models.ForeignKey(
        TicketBooking,
        on_delete=models.CASCADE,
        related_name="tickets",
        db_index=True,
        help_text="The parent transactional ledger configuration header mapping this ticket asset",
    )

    seat = models.ForeignKey(
        Seat,
        on_delete=models.SET_NULL,
        related_name="tickets",
        null=True,
        blank=True,
        db_index=True,
        help_text="The physical asset seat coordinate row currently assigned inside the vehicle model",
    )

    checked_in_by = models.ForeignKey(
        UserAccount,
        on_delete=models.SET_NULL,
        related_name="processed_ticket_checkins",
        null=True,
        blank=True,
        db_index=True,
        help_text="The terminal controller or conductor user who scanned and cleared this ticket at the gate",
    )

    # ========================================================================
    # PASSENGER & SEAT SNAPSHOT METADATA
    # ========================================================================

    seat_code = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="Immutable string copy snapshot of the seat code (e.g., A12, B04) to prevent historic data loss",
    )

    passenger_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Full name coordinates of the physical individual traveling on this seat pass",
    )

    passenger_phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^\+?[0-9\s\-]{7,20}$",
                message="Passenger phone number format specification is invalid",
            )
        ],
        help_text="Contact mobile string sequence belonging specifically to the passenger assigned to this seat",
    )

    passenger_type = models.CharField(
        max_length=20,
        choices=PASSENGER_TYPE_CHOICES,
        default="ADULT",
        db_index=True,
        help_text="The demographic price calculation category class mapped to this passenger",
    )

    # ========================================================================
    # FINANCIAL LEDGER ARITHMETICS
    # ========================================================================

    base_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="The unmodified standard entry-level price allocated for this seat routing specification",
    )

    discount_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text="The total deducted monetary value derived from promotional voucher campaigns or concession tiers",
    )

    final_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="The actual final commercial revenue collected for this specific seat item (base_price - discount_amount)",
    )

    # ========================================================================
    # SCANNING HARDWARE TOKENS & UNIQUE KEYS
    # ========================================================================

    qr_code = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        help_text="Cryptographically unique text token string rendered into QR graphic matrix blocks for mobile phone scanning",
    )

    barcode = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        help_text="Cryptographically unique text token string rendered into physical 1D barcode layouts for printed thermal stubs",
    )

    # ========================================================================
    # LIFECYCLE CONTROLS & CHRONOLOGY
    # ========================================================================

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="ACTIVE",
        db_index=True,
        help_text="The current functional stage state tracking this boarding pass ticket asset",
    )

    checked_in_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timezone-aware timestamp logging exactly when the customer successfully cleared bến bãi checkpoint gates",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this specific individual boarding line ticket seat node was generated",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when parameters inside this boarding pass item were last modified (Trigger handled in DDL)",
    )

    class Meta:
        db_table = "tickets"
        verbose_name = _("Passenger Ticket")
        verbose_name_plural = _("Passenger Tickets")
        ordering = ["booking", "seat_code", "id"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Direct database CHECK constraint matching CONSTRAINT chk_ticket_status
            models.CheckConstraint(
                condition=models.Q(
                    status__in=[
                        "ACTIVE",
                        "USED",
                        "CANCELLED",
                        "REFUNDED",
                        "EXCHANGED",
                        "EXPIRED",
                    ]
                ),
                name="chk_ticket_status",
            ),
            # Financial data integrity check: Math logic confirmation
            models.CheckConstraint(
                condition=models.Q(final_price__gte=0)
                & models.Q(base_price__gte=0)
                & models.Q(discount_amount__gte=0),
                name="chk_ticket_prices_positive",
            ),
        ]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Partial conditional index optimizing barcode hardware lookups matching CREATE INDEX idx_tickets_qr
            # Note: Django natively handles conditional mapping via condition parameter inside models.Index
            models.Index(
                fields=["qr_code"],
                name="idx_tickets_qr_partial",
                condition=models.Q(qr_code__isnull=False),
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"Ticket #{self.id} -> Seat: {self.seat_code or 'Unassigned'} | Pass: {self.passenger_name or 'Anonymous'} [{self.status}]"

    # ========================================================================
    # BUSINESS LOGIC & TERMINAL CHECK-IN GATE METHODS
    # ========================================================================

    def clean(self):
        """
        Application-layer financial checking rules before database serialization locks.
        """
        super().clean()

        # Mathematical integrity check
        if (
            self.base_price is not None
            and self.discount_amount is not None
            and self.final_price is not None
        ):
            calculated_price = self.base_price - self.discount_amount
            if calculated_price < 0:
                calculated_price = 0
            if abs(self.final_price - calculated_price) > 0.01:
                raise ValidationError(
                    {
                        "final_price": _(
                            "Financial Arithmetic Discrepancy: Final price must match (base_price - discount_amount) calculation flow."
                        )
                    }
                )

    def execute_terminal_gate_checkin(self, gate_staff_user):
        """
        Processes real-time electronic check-in verification when a client scans their pass
        at the physical vehicle platform platform entrance.

        Args:
            gate_staff_user: UserAccount model instance representing the checking employee
        """
        if self.status != "ACTIVE":
            raise ValidationError(
                _(
                    "Gate Clearance Error: Boarding pass is invalid. Current ticket lifecycle token is: {}"
                ).format(self.status)
            )

        from django.utils import timezone

        self.status = "USED"
        self.checked_in_at = timezone.now()
        self.checked_in_by = gate_staff_user
        self.save(
            update_fields=["status", "checked_in_at", "checked_in_by", "updated_at"]
        )

        # Analytics hook point: Dispatch real-time telematics payload data signals out to
        # passenger manifest dashboards alerting dispatchers that seat position is officially occupied.
