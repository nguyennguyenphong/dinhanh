# ============================================================================
# FILE: apps/bookings/models.py
# Ticket Operational Exchange Ledger Models
# ============================================================================

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TicketExchange(models.Model):
    """
    TicketExchange model managing the operational lifecycle of passenger boarding pass mutations.

    Features:
    - Ticket Bridge Architecture: Connects an original revoked ticket node with a newly minted replacement ticket
    - Unique Exchange Reference: Enforces system-wide unique lookup transaction voucher indexes
    - High-Precision Surcharges: Leverages Decimal fields to track dynamic administrative modification fees
    - Automated Inventory Release: Rebounds old seat layout coordinates back into general pools upon confirmation

    Statuses:
    - PENDING: Exchange record initialized by agent counter, target new seat locked temporarily
    - COMPLETED: Modification fees cleared, old ticket permanently revoked, new ticket officially activated
    - REJECTED: Modification request denied or abandoned, old ticket remains active, temporary hold released

    Example:
        # Create a new pending ticket swap record
        exchange_log = TicketExchange.objects.create(
            original_ticket_id=45120,
            new_ticket_id=45299,
            exchange_code='EXC-20260530-K891',
            reason='Passenger requested later departure schedule time due to flight delay',
            fee=30000.00,
            status='PENDING'
        )
    """

    STATUS_CHOICES = (
        (
            "PENDING",
            _("Pending - Rerouting initialized, awaiting fee payment settlement"),
        ),
        (
            "COMPLETED",
            _("Completed - Fee cleared, original ticket revoked, new ticket activated"),
        ),
        (
            "REJECTED",
            _("Rejected - Exchange request cancelled, original ticket state retained"),
        ),
    )

    # Using BigAutoField matches BIGSERIAL primary key target requirements
    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS (TICKET SWAP BRIDGE)
    # ========================================================================

    original_ticket = models.ForeignKey(
        "customers_tickets.Ticket",
        on_delete=models.PROTECT,
        related_name="exchange_as_original",
        db_index=True,
        help_text="The historical core passenger boarding pass targeted to be revoked and replaced",
    )

    new_ticket = models.ForeignKey(
        "customers_tickets.Ticket",
        on_delete=models.SET_NULL,
        related_name="exchange_as_new",
        null=True,
        blank=True,
        db_index=True,
        help_text="The newly minted replacement boarding pass ticket issued under this mutation pipeline",
    )

    processed_by = models.ForeignKey(
        "accounts.UserAccount",
        on_delete=models.SET_NULL,
        related_name="processed_exchanges",
        null=True,
        blank=True,
        db_index=True,
        help_text="The ticket box clerk or helpdesk user account executing this rerouting transition",
    )

    # ========================================================================
    # IDENTITY CODE & TRANSACTION DETAILS
    # ========================================================================

    exchange_code = models.CharField(
        max_length=30,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[A-Z0-9\-_]+$",
                message="Exchange voucher code must contain only uppercase letters, numbers, hyphens, and underscores",
            )
        ],
        help_text="Unique operational index token used for tracking outbound modification vouchers (e.g., EXC-9921-X)",
    )

    reason = models.TextField(
        null=True,
        blank=True,
        help_text="Explicit text statement provided explaining why the customer requested a route mutation",
    )

    # ========================================================================
    # FINANCIAL ARITHMETIC SURCHARGES
    # ========================================================================

    fee = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text="The administrative surcharge penalty penalty assessed for processing the ticket modification",
    )

    # ========================================================================
    # WORKFLOW PROGRESSION LIFECYCLES
    # ========================================================================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
        db_index=True,
        help_text="The progression phase state tracking this swap log through verification and payment gates",
    )

    # ========================================================================
    # SYSTEM AUDITS
    # ========================================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this operational modification log row was opened inside the database core",
    )

    class Meta:
        db_table = "ticket_exchanges"
        verbose_name = _("Ticket Exchange Ledger")
        verbose_name_plural = _("Ticket Exchange Ledgers")
        ordering = ["-created_at", "exchange_code"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Direct database-level CHECK constraint enforcing workflow state security matrices
            models.CheckConstraint(
                condition=models.Q(status__in=["PENDING", "COMPLETED", "REJECTED"]),
                name="chk_exchange_status_rules",
            ),
            # Financial data integrity check: Fee scale cannot physically exist below absolute zero
            models.CheckConstraint(
                condition=models.Q(fee__gte=0), name="chk_exchange_fee_positive"
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"[{self.exchange_code}] Ticket #{self.original_ticket_id} -> #{self.new_ticket_id or '??'} ({self.status})"

    # ========================================================================
    # BUSINESS METRICS & MUTATION STATE ENGINE WORKFLOWS
    # ========================================================================

    def clean(self):
        """
        Application-layer validation parsing matrix compliance before database serialization locks.
        """
        super().clean()

        if (
            self.original_ticket_id
            and self.new_ticket_id
            and self.original_ticket_id == self.new_ticket_id
        ):
            raise ValidationError(
                {
                    "new_ticket": _(
                        "Data Logic Error: Target replacement ticket cannot be physically identical to the source original ticket."
                    )
                }
            )

        if self.fee and self.fee < 0:
            raise ValidationError(
                {
                    "fee": _(
                        "Financial validation error: Modification processing surcharges cannot reflect negative parameters."
                    )
                }
            )

    def execute_exchange_confirmation(self, administrative_staff_user=None):
        """
        Executes the atomic workflow confirmation switch swap.
        Permanently revokes the old ticket, activates the new ticket, and clears state lines.
        """
        if self.status != "PENDING":
            raise ValidationError(
                _(
                    "Workflow Block: This exchange entry ledger line has already bypassed its reviewable PENDING state."
                )
            )

        if not self.new_ticket:
            raise ValidationError(
                _(
                    "Operational Error: Cannot complete migration flow without an explicitly attached new replacement ticket."
                )
            )

        # 1. Update the transactional metadata attributes
        self.status = "COMPLETED"
        if administrative_staff_user:
            self.processed_by = administrative_staff_user
        self.save(update_fields=["status", "processed_by"])

        # 2. Mutate the status flag of the original source ticket to EXCHANGED (releases old seat map)
        self.original_ticket.status = "EXCHANGED"
        self.original_ticket.save(update_fields=["status", "updated_at"])

        # 3. Elevate the state flag of the newly minted ticket to ACTIVE (permanently locks new seat)
        self.new_ticket.status = "ACTIVE"
        self.new_ticket.save(update_fields=["status", "updated_at"])

        # Core telematics integration point: Emit event to bến bãi tracking systems here
        # to refresh passenger manifests for both affected trips in real-time.

    def execute_exchange_rejection(self, notes_reason=""):
        """
        Rejects or aborts the initialized modification flow.
        Restores old ticket validity and marks the exchange document line as dead.
        """
        if self.status != "PENDING":
            raise ValidationError(
                _(
                    "State Machine Error: This mutation pipeline record is already closed or locked."
                )
            )

        self.status = "REJECTED"
        if notes_reason:
            self.reason = (
                f"{self.reason}\n[Rejection Reason]: {notes_reason}"
                if self.reason
                else f"[Rejection Reason]: {notes_reason}"
            )
        self.save(update_fields=["status", "reason"])

        # If a new ticket had been prepared and placed on hold, drop its status here
        if self.new_ticket:
            self.new_ticket.status = "CANCELLED"
            self.new_ticket.save(update_fields=["status", "updated_at"])
