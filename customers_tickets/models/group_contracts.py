# ============================================================================
# FILE: apps/bookings/models.py
# Group Contract Commercial B2B Management Models
# ============================================================================

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class GroupContract(models.Model):
    """
    GroupContract model managing high-volume B2B charting contracts and corporate block bookings.

    Features:
    - Multi-tenancy: Securely partitioned and isolated via tenant_id
    - Unique Contract Token: Human-readable alphanumeric business reference code enforced system-wide
    - Capacity Auditing: Tracks exact requested seat allocation counts via SmallIntegerField mapping
    - Dual-Stage Financials: Monitors gross contract debt against initialization deposit thresholds
    - Media File Linking: Stores remote storage URLs (e.g., AWS S3, Google Cloud Storage) for scanned PDF paper contracts

    Statuses:
    - DRAFT: Initial negotiations outline, inventory is unreserved or temporarily loose held
    - CONFIRMED: Deposit successfully processed, commercial inventory permanently locked for the group
    - CANCELLED: Contract voided, financial retention rules applied, seat blocks returned to general sales
    - COMPLETED: Journey executed successfully, final financial balances cleared and closed

    Example:
        # Create a corporate B2B chart contract draft line
        contract = GroupContract.objects.create(
            tenant_id=1,
            contract_code='CTR-20260530-ACME',
            customer_name='ACME Corporation Joint Stock',
            customer_phone='+84912345678',
            customer_tax_code='0102030405',
            trip_id=482,
            seat_count=25,
            total_amount=7500000.00,
            deposit_amount=2000000.00,
            status='DRAFT'
        )
    """

    STATUS_CHOICES = (
        ("DRAFT", _("Draft - Negotiation planning phase, loose allocation hold")),
        (
            "CONFIRMED",
            _("Confirmed - Deposit cleared, passenger block inventory secured"),
        ),
        (
            "CANCELLED",
            _("Cancelled - Contract terminated, seat allocation blocks released"),
        ),
        (
            "COMPLETED",
            _("Completed - Journey finalized, invoice balances cleared and locked"),
        ),
    )

    id = models.AutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS & MULTI-TENANCY
    # ========================================================================

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        default=1,
        related_name="group_contracts",
        db_index=True,
        help_text="Tenant corporate owner who holds commercial rights over this group charter ledger",
    )

    trip = models.ForeignKey(
        "trips.Trip",
        on_delete=models.PROTECT,
        related_name="group_contracts",
        db_index=True,
        help_text="The destination commercial trip vehicle journey assigned for this group booking",
    )

    created_by = models.ForeignKey(
        "accounts.UserAccount",
        on_delete=models.SET_NULL,
        related_name="created_contracts",
        null=True,
        blank=True,
        db_index=True,
        help_text="The sales agent or corporate account manager who generated this document ledger line",
    )

    # ========================================================================
    # UNIQUE BUSINESS CODES & CUSTOMER CRM METADATA
    # ========================================================================

    contract_code = models.CharField(
        max_length=30,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[A-Z0-9\-_]+$",
                message="Contract code must contain only uppercase letters, numbers, hyphens, and underscores",
            )
        ],
        help_text="Unique business reference ledger code tracking this contract sheet (e.g., CTR-2026-001X)",
    )

    customer_name = models.CharField(
        max_length=255,
        help_text="Full legal individual name or corporate company text purchasing this block contract",
    )

    customer_phone = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r"^\+?[0-9\s\-]{7,20}$",
                message="Customer contact phone number format specification is invalid",
            )
        ],
        help_text="Primary communication phone sequence used for B2B accounts follow-up operations",
    )

    customer_email = models.EmailField(
        max_length=254,
        null=True,
        blank=True,
        help_text="Electronic mail node endpoint used for automatic billing and invoice dispatch lines",
    )

    customer_tax_code = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="Government statutory tax identifier token for corporate legal receipt generation (VAT invoice)",
    )

    # ========================================================================
    # LOGISTICS METRICS & FINANCIAL LEDGER ARITHMETICS
    # ========================================================================

    seat_count = models.SmallIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Total aggregate allocation number of physical seat inventory chunks reserved by the group",
    )

    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="The full negotiated gross contract value currency rate calculated for this contract line",
    )

    deposit_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text="The initialization payment threshold required to transition the document out of Draft status",
    )

    # ========================================================================
    # LIFECYCLE CONTROLS & MEDIA ASSETS
    # ========================================================================

    deposit_paid_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timezone-aware timestamp logging exactly when database confirmed receipt of deposit funds",
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="DRAFT",
        db_index=True,
        help_text="The structural workflow state tracking this B2B lease through settlement and execution gates",
    )

    contract_file = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="Cloud object storage URL file path string pointing to the digital scan copy of the signed contract PDF file",
    )

    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Miscellaneous business negotiation notes, special pickup itineraries, or specific refund exemption logs",
    )

    # ========================================================================
    # SYSTEM AUDITS
    # ========================================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this corporate charter contract was first registered inside the core DB",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when parameters inside this B2B ledger sheet were last modified",
    )

    class Meta:
        db_table = "group_contracts"
        verbose_name = _("Group Contract")
        verbose_name_plural = _("Group Contracts")
        ordering = ["-created_at", "contract_code"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Direct database-level CHECK constraint enforcing workflow state taxonomy
            models.CheckConstraint(
                condition=models.Q(
                    status__in=["DRAFT", "CONFIRMED", "CANCELLED", "COMPLETED"]
                ),
                name="chk_group_contract_status_rules",
            ),
            # Financial data integrity check: Math bounds verification
            models.CheckConstraint(
                condition=models.Q(total_amount__gte=0)
                & models.Q(deposit_amount__gte=0),
                name="chk_contract_amounts_positive",
            ),
            # Logic check: Deposit parameter cannot mathematically bypass total invoice numbers
            models.CheckConstraint(
                condition=models.Q(deposit_amount__lte=models.F("total_amount")),
                name="chk_contract_deposit_limit",
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"[{self.contract_code}] {self.customer_name} -> Seats: {self.seat_count} ({self.status})"

    # ========================================================================
    # B2B BUSINESS WORKFLOW & FINANCIAL ADVANCEMENT METHODS
    # ========================================================================

    def clean(self):
        """
        Application-layer validation checking matrix compliance before database serialization locks.
        """
        super().clean()

        if self.total_amount is not None and self.deposit_amount is not None:
            if self.deposit_amount > self.total_amount:
                raise ValidationError(
                    {
                        "deposit_amount": _(
                            "Accounting Logic Error: Milestone deposit amount cannot physically exceed the contract gross total amount."
                        )
                    }
                )

        if self.seat_count and self.seat_count <= 0:
            raise ValidationError(
                {
                    "seat_count": _(
                        "Logistics Error: Block allocation requests must allocate 1 or more seats."
                    )
                }
            )

    def execute_deposit_clearance(self):
        """
        Registers real-world deposit bank clearance, logging mốc thời gian,
        and escalates document tracking state from DRAFT to CONFIRMED.
        """
        if self.status != "DRAFT":
            raise ValidationError(
                _(
                    "Workflow Block: Deposit clearance milestone can only be executed on DRAFT stage contracts."
                )
            )

        from django.utils import timezone

        self.status = "CONFIRMED"
        self.deposit_paid_at = timezone.now()
        self.save(update_fields=["status", "deposit_paid_at", "updated_at"])

        # Dispatch inventory signal point: Automatically transition dynamic trip capacity
        # matrices to reflect that these block seats are locked down and shielded from public B2C retail booking engines.

    def finalize_contract_completion(self):
        """
        Closes out the legal agreement ledger line once final payments are audited and
        the transport journey has completed operations.
        """
        if self.status != "CONFIRMED":
            raise ValidationError(
                _(
                    "Operational Error: Contracts cannot transition to COMPLETED without going through CONFIRMED status."
                )
            )

        if not self.contract_file:
            raise ValidationError(
                {
                    "contract_file": _(
                        "Compliance Audit Alert: Cannot close out a contract line without attaching the signed contract PDF scan copy file."
                    )
                }
            )

        self.status = "COMPLETED"
        self.save(update_fields=["status", "updated_at"])

    def execute_contract_cancellation(self, void_reason):
        """
        Aborts the B2B agreement line, frees up vehicle inventory blocks, and logs operational reason text.

        Args:
            void_reason: String note detailing background text context
        """
        if self.status in ["CANCELLED", "COMPLETED"]:
            raise ValidationError(
                _(
                    "State Machine Error: This group contract record is already closed or terminated."
                )
            )

        self.status = "CANCELLED"
        append_note = f"[Contract Cancelled]: {void_reason}"
        self.notes = f"{self.notes}\n{append_note}" if self.notes else append_note
        self.save(update_fields=["status", "notes", "updated_at"])

        # Downstream inventory hook point: Instantly release all blocked seats back into
        # the public retail pool to recover potential unsold ticket losses.
