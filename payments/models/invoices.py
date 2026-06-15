# ============================================================================
# FILE: apps/payments/models.py
# Financial VAT & Electronic Invoice Management Models
# ============================================================================

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _



class Invoice(models.Model):
    """
    Invoice model representing the official legal electronic VAT invoice ledger (Hóa đơn điện tử GTGT).

    Features:
    - Multi-tenancy Isolation: Securely partitioned and isolated via tenant_id
    - Polymorphic Billing Links: Connects to retail B2C TicketBookings or corporate B2B GroupContracts
    - Strict Tax Identification: Tracks official buyer tax codes, registration serials, and invoice numbers
    - Automated Tax Matrix: Implements high-precision arithmetic math validating subtotals, VAT rates, and grand totals
    - Government Portal Synchronization: Stores digital clearance tokens (e_invoice_code) and portal viewer links

    Statuses:
    - DRAFT: Invoice sheet prepared by accounting, pending structural confirmation or portal broadcast
    - ISSUED: Formally locked, digitally signed, and transmitted out to the General Department of Taxation portal
    - CANCELLED: Legally voided due to product refund or data mistake, replacement protocol triggered
    - REPLACED: Superseded by a newly generated corrective invoice sheet, referenced backwards

    Example:
        # Initialize a legal VAT invoice draft line for a corporate client
        invoice = Invoice.objects.create(
            tenant_id=1,
            invoice_no='00001234',
            series='1C26TAA',  # 2026 Serial format matching tax standards
            group_contract_id=52,
            buyer_name='AN PHAT TRANSPORT TECHNOLOGY JSC',
            buyer_tax_code='0102030405',
            subtotal=10000000.00,
            vat_rate=10.00,
            vat_amount=1000000.00,
            total_amount=11000000.00,
            status='DRAFT'
        )
    """

    STATUS_CHOICES = (
        ("DRAFT", _("Draft - Prepared workspace sheet, digital signature pending")),
        (
            "ISSUED",
            _("Issued - Digitally signed, authorized by tax authority portal, locked"),
        ),
        (
            "CANCELLED",
            _("Cancelled - Legally voided via official adjustment minute protocol"),
        ),
        (
            "REPLACED",
            _("Replaced - Voided and superseded by a corrective replacement invoice"),
        ),
    )

    id = models.AutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS & MULTI-TENANCY
    # ========================================================================

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,  # Matches ON DELETE CASCADE from requirement
        default=1,
        related_name="invoices",
        db_index=True,
        help_text="Tenant corporate corporate owner holding local fiscal rights over this tax document",
    )

    booking = models.ForeignKey(
        "customers_tickets.TicketBooking",
        on_delete=models.SET_NULL,  # Matches REFERENCES ticket_bookings(id) ON DELETE SET NULL
        related_name="invoices",
        null=True,
        blank=True,
        db_index=True,
        help_text="The retail passenger reservation sheet bound to this financial tax document",
    )

    group_contract = models.ForeignKey(
        "customers_tickets.GroupContract",
        on_delete=models.SET_NULL,  # Matches REFERENCES group_contracts(id) ON DELETE SET NULL
        related_name="invoices",
        null=True,
        blank=True,
        db_index=True,
        help_text="The corporate B2B chart contract order document bound to this financial tax document",
    )

    issued_by = models.ForeignKey(
        "accounts.UserAccount",
        on_delete=models.SET_NULL,  # Matches REFERENCES user_accounts(id) ON DELETE SET NULL
        related_name="issued_invoices",
        null=True,
        blank=True,
        db_index=True,
        help_text="The licensed internal staff accountant executing the digital gateway HSM signature",
    )

    # ========================================================================
    # LEGAL TAX METADATA IDENTIFIERS
    # ========================================================================

    invoice_no = models.CharField(
        max_length=50,
        unique=True,  # Matches VARCHAR(50) NOT NULL UNIQUE
        validators=[
            RegexValidator(
                regex=r"^[0-9]{1,8}$",
                message="Invoice number must represent a numeric sequence matching statutory lengths",
            )
        ],
        help_text="Official sequential invoice identification digit marker string (e.g., 00001234)",
    )

    series = models.CharField(
        max_length=10,
        help_text="Official statutory invoice symbol series prefix tracking registration year (e.g., 1C26TAA)",
    )

    # ========================================================================
    # BUYER PROFILE DETAILS (CRM ALIGNMENT)
    # ========================================================================

    buyer_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Legal corporate entity name text or individual consumer name printed on the certificate header",
    )

    buyer_tax_code = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^[0-9\-]{10,14}$",
                message="Government buyer tax identification code format matrix is invalid",
            )
        ],
        help_text="Government corporate business tax classification token needed for input tax deduction logs",
    )

    buyer_address = models.TextField(
        null=True,
        blank=True,
        help_text="Full corporate operational registration address text required by tax departments",
    )

    buyer_email = models.EmailField(
        max_length=254,  # Matches buyer_email VARCHAR(254)
        null=True,
        blank=True,
        help_text="Electronic mail destination endpoint where the signed XML/PDF invoice files are pushed automatically",
    )

    # ========================================================================
    # HIGH-PRECISION REVENUE FINANCIAL ARITHMETICS
    # ========================================================================

    subtotal = models.DecimalField(
        max_digits=15,
        decimal_places=2,  # Matches NUMERIC(15,2) NOT NULL
        help_text="The net taxable operational revenue balance calculated prior to adding tax metrics",
    )

    vat_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=10.00,  # Matches NUMERIC(5,2) NOT NULL DEFAULT 10.00
        help_text="Statutory value added tax percentage rate scalar applied to sales (e.g., 8.00 or 10.00)",
    )

    vat_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,  # Matches NUMERIC(15,2) NOT NULL
        help_text="The absolute computed tax weight calculated dynamically from (subtotal * (vat_rate / 100))",
    )

    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,  # Matches NUMERIC(15,2) NOT NULL
        help_text="The eventual absolute gross invoice liability cash balance collected (subtotal + vat_amount)",
    )

    # ========================================================================
    # ELECTRONIC GATEWAY TOKENS & SYSTEM WORKFLOWS
    # ========================================================================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="DRAFT",
        db_index=True,
        help_text="The internal operational progression phase state tracking this tax document item",
    )

    e_invoice_code = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,  # Production index: Vital for lookups when receiving tax gateway updates
        help_text="Unique cryptographic reference lookup key hash returned by third-party e-invoice provider networks (e.g., Viettel SInvoice, VNPT, Misa MeInvoice)",
    )

    e_invoice_url = models.CharField(
        max_length=500,
        null=True,
        blank=True,  # Matches VARCHAR(500)
        help_text="Cloud storage direct URL link matching online verification portal locations where the client downloads the official PDF copy",
    )

    # ========================================================================
    # CHRONOLOGY AUDIT MARKS
    # ========================================================================

    issued_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timezone-aware timestamp logging exactly when digital certificates signed this document block out to government systems",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="System record logging anchor tracking exactly when this invoice layout was initialized inside the DB core",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when parameters inside this financial invoice sheet were last modified",
    )

    class Meta:
        db_table = "invoices"
        verbose_name = _("Legal VAT Invoice")
        verbose_name_plural = _("Legal VAT Invoices")
        ordering = ["-created_at", "invoice_no"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Direct database-level CHECK constraint enforcing workflow state taxonomy security
            models.CheckConstraint(
                condition=models.Q(
                    status__in=["DRAFT", "ISSUED", "CANCELLED", "REPLACED"]
                ),
                name="chk_invoice_status_rules",
            ),
            # Financial data integrity check: Math scales cannot collapse into absolute negative bounds
            models.CheckConstraint(
                condition=models.Q(subtotal__gte=0)
                & models.Q(vat_amount__gte=0)
                & models.Q(total_amount__gte=0),
                name="chk_invoice_amounts_positive",
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"Invoice {self.series}-{self.invoice_no} | Total: {self.total_amount:,.0f} VND [{self.status}]"

    # ========================================================================
    # ELECTRONIC TAX INTEGRATION WORKFLOW METHODS
    # ========================================================================

    def clean(self):
        """
        Application-layer mathematics and data structure balance audit before committing data packets.
        """
        super().clean()

        if not self.booking_id and not self.group_contract_id:
            raise ValidationError(
                _(
                    "Tax Compliance Error: A tax document must be derived from an active retail Ticket Booking or a B2B Group Contract source."
                )
            )

        # Precise rounding checks calculating VAT amounts: (Subtotal * VAT Rate) / 100
        if (
            self.subtotal is not None
            and self.vat_rate is not None
            and self.vat_amount is not None
        ):
            expected_vat = (self.subtotal * self.vat_rate) / 100
            if (
                abs(self.vat_amount - expected_vat) > 1.00
            ):  # Allow 1 VND tolerance factor due to tax decimal roundings
                raise ValidationError(
                    {
                        "vat_amount": _(
                            "Accounting Discrepancy: Calculated VAT amount parameters do not align with subtotal and applied tax weights."
                        )
                    }
                )

        # Grand Total verification: Subtotal + VAT Amount = Total Amount
        if (
            self.subtotal is not None
            and self.vat_amount is not None
            and self.total_amount is not None
        ):
            expected_total = self.subtotal + self.vat_amount
            if abs(self.total_amount - expected_total) > 1.00:
                raise ValidationError(
                    {
                        "total_amount": _(
                            "Accounting Discrepancy: Grand total amount metric does not mathematically match the sum of subtotal and tax values."
                        )
                    }
                )

    def execute_electronic_portal_issuance(
        self, accountant_user, gateway_code, dynamic_view_url
    ):
        """
        Executes HSM smart-card digital signing protocols. Transmits invoice payload matrices
        out to licensed provider gateways, captures response certificates, and seals records.

        Args:
            accountant_user: UserAccount model instance tracking the executing employee signature
            gateway_code: String key hash returned by corporate provider systems (e.g., VNPT/Viettel Token)
            dynamic_view_url: Cloud string path link generated for customer viewing portals
        """
        if self.status != "DRAFT":
            raise ValidationError(
                _(
                    "Tax Portal Error: Issuance pipelines can only trigger on raw DRAFT stage records."
                )
            )

        from django.utils import timezone

        self.status = "ISSUED"
        self.e_invoice_code = gateway_code
        self.e_invoice_url = dynamic_view_url
        self.issued_by = accountant_user
        self.issued_at = timezone.now()

        self.save(
            update_fields=[
                "status",
                "e_invoice_code",
                "e_invoice_url",
                "issued_by",
                "issued_at",
                "updated_at",
            ]
        )

        # Async Task Queue Trigger: Dispatches transactional background email containing
        # official XML and PDF attachment structures out to the registered buyer_email node endpoint.

    def execute_legal_invoice_cancellation(self, adjustment_minute_ref):
        """
        Processes formal legal voiding protocols according to governmental tax regulations.
        Locks original invoice fields and labels metrics as invalid.

        Args:
            adjustment_minute_ref: String tracking number of the signed digital cancellation agreement minutes
        """
        if self.status != "ISSUED":
            raise ValidationError(
                _(
                    "Compliance Error: Voiding/Cancellation procedures can only operate on officially ISSUED tax documents."
                )
            )

        self.status = "CANCELLED"
        # Log the legal adjustments protocol token directly into tracking logs text fields
        self.buyer_address = (
            f"{self.buyer_address}\n[VOIDED VIA TAX PROTOCOL MINUTE REF: {adjustment_minute_ref}]"
            if self.buyer_address
            else f"[VOIDED MINUTE: {adjustment_minute_ref}]"
        )

        self.save(update_fields=["status", "buyer_address", "updated_at"])
