# ============================================================================
# FILE: apps/logistics/models.py
# Cargo Logistics Pricing Matrix Models
# ============================================================================

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from safedelete.models import SOFT_DELETE_CASCADE, SafeDeleteModel


class CargoPriceTable(SafeDeleteModel):
    """
    CargoPriceTable model acts as the core algorithmic pricing matrix rule-sheet for logistics operations.

    Features:
    - Multi-tenancy Isolation: Securely partitioned and isolated via tenant_id.
    - Route-Specific Target Overrides: Links custom prices to distinct transit routes (or defaults global rules if NULL).
    - Multi-Dimensional Metrics Bounds: Filters execution based on cargo taxonomy types, weights, and spatial volume ranges.
    - Variable Tariff Units Matrix: Supports calculations via mass metrics (KG), spatial sizes (M3), flat-fees, or full journeys.

    Cargo Types:
    - NORMAL: General dry non-perishable freight packages (e.g., clothes, paperwork boxes).
    - FRAGILE: Glassware, delicate electronics components, or porcelain items demanding special padding.
    - LIQUID: Bottled materials or fluids needing secondary containment and spill protection protocols.
    - FROZEN: Cold-chain temperature-controlled biological perishables, ice creams, or fresh meat boxes.
    - OVERSIZED: Bulky dimensions surpassing standard chassis compartments (e.g., motorbikes, furniture).
    - HAZARDOUS: Flammable materials, pressurized aerosol canisters, or lithium batteries demanding safety decals.

    Price Units:
    - PER_KG: Dynamic cost factor scaled iteratively per individual kilogram of package mass.
    - PER_TRIP: Consolidated transportation cost applied entirely per journey vehicle dispatch execution.
    - FLAT: Fixed standard envelope tariff voucher point independent of shape, volume, or weight constraints.
    - PER_M3: Spatial volumetric cước structure scaled per cubic meter capacity occupied in freight decks.

    Example:
        # Create a rule sheet charging 5,000 VND per KG for Normal items on Route #12 between 10kg and 50kg
        rule = CargoPriceTable.objects.create(
            tenant_id=1,
            route_id=12,
            cargo_type='NORMAL',
            min_weight=10.00,
            max_weight=50.00,
            price=5000.00,
            price_unit='PER_KG'
        )
    """

    _safedelete_policy = SOFT_DELETE_CASCADE

    CARGO_TYPE_CHOICES = (
        ("NORMAL", _("Normal - Standard dry non-perishable general parcel boxes")),
        (
            "FRAGILE",
            _(
                "Fragile - Delicate breakable items requiring specialized shock protection"
            ),
        ),
        (
            "LIQUID",
            _(
                "Liquid - Fluids or chemical barrels demanding secondary containment sets"
            ),
        ),
        ("FROZEN", _("Frozen - Cold-chain climate-controlled thermal freight lines")),
        (
            "OVERSIZED",
            _(
                "Oversized - Volumetric bulky assets exceeding standard luggage compartments"
            ),
        ),
        (
            "HAZARDOUS",
            _("Hazardous - Regulated combustible compounds or lithium cells"),
        ),
    )

    PRICE_UNIT_CHOICES = (
        (
            "PER_KG",
            _("Per Kilogram - Cost calculated multiplying scale weight increments"),
        ),
        (
            "PER_TRIP",
            _(
                "Per Trip - Structural logistics charge calculated per route execution block"
            ),
        ),
        (
            "FLAT",
            _(
                "Flat - Static invariant standard processing fee applied to parcel item unit"
            ),
        ),
        (
            "PER_M3",
            _(
                "Per Cubic Meter - Spatial dimensional volume layout multiplication rate"
            ),
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
        related_name="cargo_price_tables",
        db_index=True,
        help_text="Tenant corporate owner managing this isolated logistics tariffs configuration leaf",
    )

    route = models.ForeignKey(
        "routes.Route",
        on_delete=models.SET_NULL,
        related_name="cargo_tariffs",
        null=True,
        blank=True,
        db_index=True,
        help_text="The specific geography transport route assigned to this tariff rate. If NULL, acts as a global baseline rule.",
    )

    # ========================================================================
    # CARGO CLASSIFICATION TAXONOMY
    # ========================================================================

    cargo_type = models.CharField(
        max_length=50,
        choices=CARGO_TYPE_CHOICES,
        null=True,
        blank=True,
        db_index=True,
        help_text="The specialized transport properties group classification assigned to this matrix rule line",
    )

    # ========================================================================
    # DATA INTERSECTIONS: MASS RANGE CHECKS (NUMERIC 8,2)
    # ========================================================================

    min_weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.00)],
        help_text="The inclusive lower mass boundary benchmark requirement calculated in kilograms (KG)",
    )

    max_weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.00)],
        help_text="The inclusive upper mass boundary benchmark requirement calculated in kilograms (KG)",
    )

    # ========================================================================
    # DATA INTERSECTIONS: SPATIAL CUBIC SPACE CHECKS (NUMERIC 8,3)
    # ========================================================================

    min_volume = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.000)],
        help_text="The inclusive lower spatial dimension volume check calculation threshold in cubic meters (M3)",
    )

    max_volume = models.DecimalField(
        max_digits=8,
        decimal_places=3,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.000)],
        help_text="The inclusive upper spatial dimension volume check calculation threshold in cubic meters (M3)",
    )

    # ========================================================================
    # MONETARY TARIFF COEFFICIENTS & ARITHMETICS
    # ========================================================================

    price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.00)],
        help_text="The gross core billing tariff coefficient rate value assigned to this rule setup configuration",
    )

    price_unit = models.CharField(
        max_length=20,
        choices=PRICE_UNIT_CHOICES,
        default="PER_KG",
        db_index=True,
        help_text="The evaluation formula methodology applied to calculate eventual final customer parcel invoice values",
    )

    # ========================================================================
    # WORKFLOW CONTROLS & LIFECYCLE
    # ========================================================================

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Active validation switch flag. Turning this off flags the matching arithmetic engine to skip evaluating this row entry",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this logistics tariff row rule was opened inside the core database layout",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when structural parameters inside this dynamic tariff node were last modified",
    )

    class Meta:
        db_table = "cargo_price_tables"
        verbose_name = _("Cargo Pricing Rule")
        verbose_name_plural = _("Cargo Pricing Rules")
        ordering = ["tenant_id", "route_id", "cargo_type", "min_weight", "price"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Direct database-level CHECK constraints matching allowed enum types
            models.CheckConstraint(
                condition=models.Q(
                    cargo_type__in=[
                        "NORMAL",
                        "FRAGILE",
                        "LIQUID",
                        "FROZEN",
                        "OVERSIZED",
                        "HAZARDOUS",
                    ]
                )
                | models.Q(cargo_type__isnull=True),
                name="chk_cargo_pricing_type_enum",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    price_unit__in=["PER_KG", "PER_TRIP", "FLAT", "PER_M3"]
                ),
                name="chk_cargo_pricing_unit_enum",
            ),
            # Logical boundary checks: Scales cannot sit in absolute negative spaces
            models.CheckConstraint(
                condition=models.Q(price__gte=0),
                name="chk_cargo_pricing_value_positive",
            ),
            # High-integrity matrix range rules: Minimum conditions cannot physically surpass Maximum conditions
            models.CheckConstraint(
                condition=models.Q(max_weight__gte=models.F("min_weight"))
                | models.Q(max_weight__isnull=True)
                | models.Q(min_weight__isnull=True),
                name="chk_cargo_pricing_weight_range",
            ),
            models.CheckConstraint(
                condition=models.Q(max_volume__gte=models.F("min_volume"))
                | models.Q(max_volume__isnull=True)
                | models.Q(min_volume__isnull=True),
                name="chk_cargo_pricing_volume_range",
            ),
        ]

    def __str__(self):
        """String representation"""
        route_label = f"Route #{self.route_id}" if self.route_id else "GLOBAL BASELINE"
        type_label = self.cargo_type or "ALL_TYPES"
        return f"Tenant {self.tenant_id} - [{route_label}] | {type_label} | {self.price:,.0f} VND/{self.price_unit}"

    # ========================================================================
    # ALGORITHMIC LOGISTICS CALCULATORS & COMPLEX VALIDATIONS
    # ========================================================================

    def clean(self):
        """
        Application-layer range intersection validations prior to saving.
        """
        super().clean()

        # 1. Validation logic for Weight ranges
        if self.min_weight is not None and self.max_weight is not None:
            if self.min_weight > self.max_weight:
                raise ValidationError(
                    {
                        "max_weight": _(
                            "Matrix Discrepancy Error: Max evaluation weight cannot physically sit below min weight parameters."
                        )
                    }
                )

        # 2. Validation logic for Volume ranges
        if self.min_volume is not None and self.max_volume is not None:
            if self.min_volume > self.max_volume:
                raise ValidationError(
                    {
                        "max_volume": _(
                            "Matrix Discrepancy Error: Max spatial volume boundary cannot physically sit below min volume parameters."
                        )
                    }
                )

    def calculate_parcel_fee(self, actual_weight, actual_volume=0.000):
        """
        Core Pricing Execution: Evaluates a target parcel item's physical weight and spatial
        metrics against this rule's configurations to output gross freight logistics costs.

        Args:
            actual_weight: Decimal weight mass of the parcel in KG
            actual_volume: Decimal structural space volume of the parcel in M3

        Returns:
            Decimal (The computed financial cost for this rule component)
        """
        from decimal import Decimal

        # Convert inputs to target decimals for calculation matching
        w = Decimal(str(actual_weight))
        v = Decimal(str(actual_volume))

        if self.price_unit == "FLAT" or self.price_unit == "PER_TRIP":
            return self.price

        elif self.price_unit == "PER_KG":
            return self.price * w

        elif self.price_unit == "PER_M3":
            if v <= 0:
                raise ValueError(
                    _(
                        "Pricing Engine Error: Calculation unit is PER_M3 but package calculated volume is zero or blank."
                    )
                )
            return self.price * v

        return Decimal("0.00")
