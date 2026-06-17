# ============================================================================
# FILE: apps/payments/models.py
# Payment Transaction Ledger Models
# ============================================================================

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class Payment(BaseModel):
    """
    Payment model representing the core physical financial inflow ledger transaction.

    Features:
    - Multi-tenancy Isolation: Securely partitioned and isolated via tenant_id
    - Polymorphic Inflow Links: Bridges capital inflows from both Ticket Bookings and Cargo Consignments
    - Unique Transaction Code: Human-readable unique billing code enforced system-wide
    - Integration Gateway Tracing: Captures direct transaction references and raw callback JSONB logs
    - Operational Attribution: Maps exactly who (cashier_id) and where (branch_id) collected the funds

    Statuses:
    - PENDING: Transaction initialized, awaiting dynamic webhook pingback or cash hand-over
    - SUCCESS: Capital successfully captured and cleared into corporate accounts, invoice satisfied
    - FAILED: Gateway transaction dropped or declined by clearing networks
    - REFUNDED: Money returned to consumer via a corresponding outbound TicketRefund voucher entry
    - EXPIRED: Interactive checkout session timed out past security countdown windows

    Example:
        # Create an electronic gateway transaction entry
        tx = Payment.objects.create(
            tenant_id=1,
            payment_code='PAY-20260530-Z9X1',
            booking_id=10524,
            amount=350000.00,
            method_id=3,  # MoMo/VNPAY link
            status='PENDING',
            transaction_ref='VNPAY-TX-7782109'
        )
    """

    STATUS_CHOICES = (
        ("PENDING", _("Pending - Invoice issued, awaiting execution gateway clearing")),
        (
            "SUCCESS",
            _("Success - Settlement confirmed, capital moved into system vaults"),
        ),
        (
            "FAILED",
            _("Failed - Transaction aborted, rejected by network clearing lines"),
        ),
        (
            "REFUNDED",
            _("Refunded - Financial commercial reversal processed back to customer"),
        ),
        (
            "EXPIRED",
            _("Expired - Session gate timeout limit breached before completion"),
        ),
    )

    # Using BigAutoField matches BIGSERIAL primary key target requirements
    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS & MULTI-TENANCY
    # ========================================================================

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,  # Matches ON DELETE CASCADE from requirement
        default=1,
        related_name="payments",
        db_index=True,
        help_text="Tenant corporate owner who holds rights over this incoming cash flow ledger line",
    )

    booking = models.ForeignKey(
        "customers_tickets.TicketBooking",
        on_delete=models.SET_NULL,  # Matches REFERENCES ticket_bookings(id) ON DELETE SET NULL
        related_name="payments",
        null=True,
        blank=True,
        db_index=True,
        help_text="The passenger reservation sheet being funded by this transaction line",
    )

    consignment = models.ForeignKey(
        "consignments.Consignment",
        on_delete=models.SET_NULL,  # Soft reference mapping the consignment module link
        related_name="payments",
        null=True,
        blank=True,
        db_index=True,
        help_text="The logistics cargo consignment packet funded by this transaction line",
    )

    method = models.ForeignKey(
        "payments.PaymentMethod",
        on_delete=models.PROTECT,  # Production safety: block deleting configuration lines if transaction logs depend on it
        related_name="payments",
        db_index=True,
        help_text="The configured channel path configuration through which this capital entry cleared",
    )

    cashier = models.ForeignKey(
        "accounts.UserAccount",
        on_delete=models.SET_NULL,  # Matches REFERENCES user_accounts(id) ON DELETE SET NULL
        related_name="collected_payments",
        null=True,
        blank=True,
        db_index=True,
        help_text="The offline front-office clerk or counter agent who hand-received the cash asset",
    )

    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,  # Matches REFERENCES branches(id) ON DELETE SET NULL
        related_name="branch_payments",
        null=True,
        blank=True,
        db_index=True,
        help_text="The physical branch terminal hub office housing the cashier who logged the funds",
    )

    # ========================================================================
    # IDENTITY CODE & FINANCIAL METRICS
    # ========================================================================

    payment_code = models.CharField(
        max_length=30,
        unique=True,  # Matches VARCHAR(30) NOT NULL UNIQUE
        validators=[
            RegexValidator(
                regex=r"^[A-Z0-9\-_]+$",
                message="Payment billing code must contain only uppercase letters, numbers, hyphens, and underscores",
            )
        ],
        help_text="Unique system transaction lookup token key code (e.g., INV-2026-99A8X)",
    )

    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,  # Matches NUMERIC(15,2) NOT NULL
        help_text="The net currency scalar balance captured or requested under this specific billing invoice",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
        db_index=True,
        help_text="The current verification phase tracking this incoming payment execution",
    )

    # ========================================================================
    # DIGITAL GATEWAY PAYLOADS & TELEMETRY INDEXES
    # ========================================================================

    transaction_ref = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,  # Production index: Essential for lookups inside dynamic payment gateway callbacks
        help_text="The external unique identification index string returned from bank gateway clearing networks",
    )

    # Native PostgreSQL JSONB architecture integration
    gateway_response = models.JSONField(
        default=dict,
        help_text="Raw JSON database tree mapping the absolute unedited telemetry response packet emitted by IPN callback webhooks",
    )

    # ========================================================================
    # CHRONOLOGY METRICS & AUDITS
    # ========================================================================

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timezone-aware timestamp logging exactly when funds cleared gateway validation protocols",
    )

    class Meta:
        db_table = "payments"
        verbose_name = _("Payment Transaction")
        verbose_name_plural = _("Payment Transactions")
        ordering = ["-created_at", "payment_code"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Direct database-level CHECK constraint matching CONSTRAINT chk_payment_status
            models.CheckConstraint(
                condition=models.Q(
                    status__in=["PENDING", "SUCCESS", "FAILED", "REFUNDED", "EXPIRED"]
                ),
                name="chk_payment_status",
            ),
            # Financial safety integrity check: Collected amount cannot sit below zero bounds
            models.CheckConstraint(
                condition=models.Q(amount__gte=0), name="chk_payment_amount_positive"
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"[{self.payment_code}] Ref: {self.transaction_ref or 'N/A'} | Amount: {self.amount:,.0f} VND [{self.status}]"

    # ========================================================================
    # TRANSACTION STATE MACHINE & GATEWAY WORKFLOW METHODS
    # ========================================================================

    def clean(self):
        """
        Application-layer data alignment sanity check before committing records.
        """
        super().clean()

        if not self.booking_id and not self.consignment_id:
            raise ValidationError(
                _(
                    "Financial Source Error: An inflow invoice line must be linked to at least one Ticket Booking or Cargo Consignment source."
                )
            )

        if self.amount and self.amount <= 0:
            raise ValidationError(
                {
                    "amount": _(
                        "Financial Data Error: Inbound transaction amount value metrics must be positive figures."
                    )
                }
            )

    def execute_successful_settlement(self, external_ref, raw_callback_data=None):
        """
        Processes successful clearance confirmation when real-world funds lock into bank accounts.
        Updates internal chronology data markers and executes down-stream business cascade loops.

        Args:
            external_ref: String tracking index from the clearing gateway bank (e.g., Napas/Momo ID)
            raw_callback_data: Dict mapping the complete webhook telemetry packet for JSONB logging
        """
        if self.status == "SUCCESS":
            return  # Idempotency safety: Prevent duplicate callback processing execution loops

        if self.status not in ["PENDING", "EXPIRED"]:
            raise ValidationError(
                _(
                    "State Machine Block: Cannot clear transactions that have already been terminated or processed."
                )
            )

        from django.utils import timezone

        # 1. Mutate internal invoice tracking markers
        self.status = "SUCCESS"
        self.transaction_ref = external_ref
        self.paid_at = timezone.now()
        if raw_callback_data:
            self.gateway_response = raw_callback_data

        self.save(
            update_fields=[
                "status",
                "transaction_ref",
                "paid_at",
                "gateway_response",
                "updated_at",
            ]
        )

        # 2. Automated Cascade Trigger Point: Inject funding updates to parent documents
        if self.booking:
            # Invokes core payment verification method inside the TicketBooking model instance
            self.booking.capture_payment_confirmation(amount_received=self.amount)

        if self.consignment:
            # Invokes payment clearance state updates inside the dynamic Cargo system
            self.consignment.mark_as_paid_inflow(amount_received=self.amount)

    def execute_failure_termination(self, failure_response_packet):
        """
        Marks an interactive gateway payment request line as dead or declined by networks.

        Args:
            failure_response_packet: Dict mapping the telemetry debug log packet for auditing
        """
        if self.status in ["SUCCESS", "REFUNDED"]:
            raise ValidationError(
                _(
                    "Accounting Audit Error: Cannot drop an invoice line that has already completed settlement clearance."
                )
            )

        self.status = "FAILED"
        if failure_response_packet:
            self.gateway_response = failure_response_packet
        self.save(update_fields=["status", "gateway_response", "updated_at"])
