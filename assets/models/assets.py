# ============================================================================
# FILE: apps/inventory/models.py
# Fixed Asset Management & Depreciation Ledger Models
# ============================================================================

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Asset(models.Model):
    """
    Asset model governing the entire lifecycle, allocation, and depreciation balance sheet of corporate property.

    Features:
    - Multi-tenancy Isolation: Multi-tenant partitioned data scoped securely with local unique code matrices.
    - Asset Operational Tracking: Maps possession chains across organizational branches and responsible employees.
    - Financial Depreciation Engine: Monitors cost basis vs. current book values using active annualized decay rates.
    - Lifecycle State Machine: Governs transitions across active use, garage repairs, or final write-offs.

    Statuses:
    - IN_USE: Active operational status, generating value or deployment benefits for the current branch.
    - MAINTENANCE: Stalled out of line operations, currently undergoing repairs inside garage facilities.
    - DISPOSED: Safely retired from inventory books via public auction scrap sales or physical destruction.
    - LOST: Unaccounted for inventory leakage, flagged by auditing teams for insurance or liability review.
    - TRANSFERRED: Temporarily locked mid-transit during relocation workflows moving between physical branches.

    Example:
        # Register a newly purchased heavy-duty diagnostic scanner tool
        asset = Asset.objects.create(
            tenant_id=1,
            code='GAR_SCAN_2026_01',
            name='OBD2 Heavy Truck Fleet Engine Diagnostic Computer',
            category_id=3,
            branch_id=2,
            purchase_date='2026-01-15',
            purchase_price=45000000.00,
            depreciation_rate=15.00,  # 15% decay per annum
            current_value=45000000.00,
            status='IN_USE'
        )
    """

    STATUS_CHOICES = (
        (
            "IN_USE",
            _("In Use - Asset is operational and deployed inside company workflows"),
        ),
        (
            "MAINTENANCE",
            _(
                "Maintenance - Asset is offline undergoing technical service or workshop repair"
            ),
        ),
        (
            "DISPOSED",
            _(
                "Disposed - Asset is retired from accounting books via scrap sale or liquidation"
            ),
        ),
        (
            "LOST",
            _(
                "Lost - Asset is missing from physical audits; flagged for financial investigation"
            ),
        ),
        (
            "TRANSFERRED",
            _(
                "Transferred - Asset is locked mid-transit during relocation between operational branches"
            ),
        ),
    )

    id = models.AutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS & MULTI-TENANCY CONTEXTS
    # ========================================================================

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        default=1,
        related_name="assets",
        db_index=True,
        help_text="Tenant corporate node holding legal data sovereignty over this inventory asset record",
    )

    category = models.ForeignKey(
        "assets.AssetCategory",
        on_delete=models.SET_NULL,
        related_name="assets",
        null=True,
        blank=True,
        db_index=True,
        help_text="The generalized asset catalog categorization group managing this inventory node",
    )

    # ========================================================================
    # LOGISTICAL CUSTODY ALLOCATIONS
    # ========================================================================

    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="assets",
        null=True,
        blank=True,
        db_index=True,
        help_text="The physical corporate branch office or garage outpost currently storing or utilizing this item",
    )

    assigned_to = models.ForeignKey(
        "hr.Employee",
        on_delete=models.SET_NULL,
        related_name="assigned_assets",
        null=True,
        blank=True,
        db_index=True,
        help_text="The primary custodian employee or operational staff driver held personally accountable for this unit",
    )

    # ========================================================================
    # CORE IDENTITY METADATA
    # ========================================================================

    code = models.CharField(
        max_length=30,
        help_text="Unique localized alphanumeric asset tag bar-code string identifier (e.g., FIX-EQUIP-0092)",
    )

    name = models.CharField(
        max_length=255,
        help_text="Full commercial description descriptive name label of the physical hardware asset unit",
    )

    serial_number = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="The raw factory hardware engraving serial number string provided by the original manufacturer",
    )

    # ========================================================================
    # FINANCIAL FISCAL LEDGER REGISTERS
    # ========================================================================

    purchase_date = models.DateField(
        null=True,
        blank=True,
        help_text="The official calendar commercial procurement date matching invoice purchase receipts",
    )

    purchase_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.00)],
        help_text="The initial gross cost basis capitalization currency amount paid to secure the asset unit",
    )

    depreciation_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)],
        help_text="The annual straight-line depreciation loss percentage scale parameter (e.g., 12.50 for 12.5% annualized decay)",
    )

    current_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.00)],
        help_text="The adjusted current net book value representing asset worth post-depreciation cycles",
    )

    warranty_expiry = models.DateField(
        null=True,
        blank=True,
        help_text="The final contractual calendar coverage expiration date logged by the manufacturer warranty agreement",
    )

    # ========================================================================
    # CONTROL LIFECYCLE MANAGEMENT & CHRONOLOGY
    # ========================================================================

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="IN_USE",
        db_index=True,
        help_text="The current active lifecycle pipeline phase state configuration tracking the hardware asset node",
    )

    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Granular physical damage tracking notes, audit log annotations, or liquidation justifications",
    )

    created_at = models.DateTimeField(
        default=models.functions.Now,
        help_text="Timezone-aware log record tracking exactly when this asset index joined the database system",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp tracking exactly when parameter attributes inside this inventory node mutated",
    )

    class Meta:
        db_table = "assets"
        verbose_name = _("Fixed Asset Record")
        verbose_name_plural = _("Fixed Asset Records")

        # Default administrative sorting scopes prioritize tracking by code hierarchies
        ordering = ["tenant_id", "code"]

        # ====================================================================
        # CONSTRAINTS & MULTI-COLUMN UNIQUE INDEX SCOPES
        # ====================================================================

        constraints = [
            # Direct database-level unique constraint matching UNIQUE (tenant_id, code)
            models.UniqueConstraint(
                fields=["tenant", "code"], name="uq_tenant_asset_code"
            ),
            # Direct database-level CHECK constraint enforcing lifecycle state taxonomy compliance
            models.CheckConstraint(
                condition=models.Q(
                    status__in=[
                        "IN_USE",
                        "MAINTENANCE",
                        "DISPOSED",
                        "LOST",
                        "TRANSFERRED",
                    ]
                ),
                name="chk_asset_lifecycle_status_enum",
            ),
            # Verification rules: monetary asset values must avoid falling below absolute zero bounds
            models.CheckConstraint(
                condition=models.Q(purchase_price__gte=0)
                | models.Q(purchase_price__isnull=True),
                name="chk_asset_purchase_price_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(current_value__gte=0)
                | models.Q(current_value__isnull=True),
                name="chk_asset_current_value_positive",
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"Tenant {self.tenant_id} | [{self.code}] {self.name} ({self.status})"

    # ========================================================================
    # PRODUCTION LIFECYCLE STATE MACHINE & FISCAL COMPUTATION ENGINES
    # ========================================================================

    def clean(self):
        """
        Application-layer structural validation auditing currency vectors and calendar dates before disk commit.
        """
        super().clean()

        # 1. Multi-Tenant Cross-Leak Shield: Validate parent categorization context matching tenant constraints
        if self.category_id and self.tenant_id != self.category.tenant_id:
            raise ValidationError(
                {
                    "category": _(
                        "Cross-Tenant Data Leak Error: Target asset category catalog belongs to a different tenant."
                    )
                }
            )

        # 2. Financial Balance Verification: Net book value cannot mathematically exceed original cost basis
        if self.purchase_price and self.current_value:
            if self.current_value > self.purchase_price:
                raise ValidationError(
                    {
                        "current_value": _(
                            "Fiscal Valuation Anomaly: Current net book value cannot exceed the historical capitalized procurement cost."
                        )
                    }
                )

        # 3. Calendar Sequence Verification: Warranty deadlines cannot expire before purchase dates occur
        if self.purchase_date and self.warranty_expiry:
            if self.warranty_expiry < self.purchase_date:
                raise ValidationError(
                    {
                        "warranty_expiry": _(
                            "Calendar Chronology Error: Manufacturer warranty expiration dates must occur after the official procurement date."
                        )
                    }
                )

    def calculate_straight_line_depreciation(self, target_year_end_date):
        """
        Calculates and updates asset net book value using straight-line depreciation algorithms.
        Formula: Depreciation Expense = Cost Basis * Annualized Decay Rate Percentage

        Args:
            target_year_end_date: Python Date object marking the target accounting financial valuation point.
        """
        if (
            not self.purchase_date
            or not self.purchase_price
            or not self.depreciation_rate
        ):
            return  # Incomplete telemetry parameter blocks, skip calculation logic

        if self.status in ["DISPOSED", "LOST"]:
            return  # Invalidate retired or missing asset metrics from depreciation schedules

        from decimal import Decimal

        # Compute total calendar days asset has been operational in company pipelines
        days_held = (target_year_end_date - self.purchase_date).days
        if days_held <= 0:
            return

        years_held = Decimal(str(days_held)) / Decimal("365.25")

        # Compute mathematical net deterioration factor weight
        total_depreciation = (
            self.purchase_price
            * (self.depreciation_rate / Decimal("100.00"))
            * years_held
        )
        computed_book_value = self.purchase_price - total_depreciation

        # Clamp valuation strictly above safe scrap threshold floors (Never decay below absolute zero)
        self.current_value = max(computed_book_value, Decimal("0.00"))
        self.save(update_fields=["current_value", "updated_at"])
