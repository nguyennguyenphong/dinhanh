# ============================================================================
# FILE: apps/routes/models.py
# Trip Pricing Tariff Management Models
# ============================================================================

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class TripPrice(BaseModel):
    """
    TripPrice model managing the commercial ticketing fare tariff matrix per route and seat type.

    Features:
    - Multi-tenancy: Isolated and partitioned securely via tenant_id
    - Dynamic Fare Strategy: Sets core prices alongside explicit child discounts per seat specification
    - Temporal Validity: Enforces calendar date ranges via valid_from and valid_to parameters
    - High-Precision Accounting: Leverages Decimal fields for all pricing matrix elements

    Seat Types:
    - SEAT: Standard sitting coach arrangement seat
    - SLEEPER: Premium flat-bed or cabin sleeper berth unit
    - VIP_SEAT: Luxury or limousine business class configuration seat

    Example:
        # Create a new tariff entry for a standard sleeper bus route
        tariff = TripPrice.objects.create(
            tenant_id=1,
            route_id=4,
            seat_type='SLEEPER',
            price=350000.00,
            child_price=250000.00,
            valid_from='2026-06-01',
            valid_to='2026-08-31',
            is_active=True
        )
    """

    SEAT_TYPE_CHOICES = (
        ("SEAT", _("Standard Sitting Seat")),
        ("SLEEPER", _("Premium Sleeper Berth")),
        ("VIP_SEAT", _("Luxury VIP Limousine Seat")),
    )

    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS & MULTI-TENANCY
    # ========================================================================

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        default=1,
        related_name="trip_prices",
        db_index=True,
        help_text="Tenant owner of this commercial pricing tariff schema",
    )

    route = models.ForeignKey(
        "routes.Route",
        on_delete=models.CASCADE,
        related_name="tariffs",
        db_index=True,
        help_text="The specific spatial transportation route this tariff applies to",
    )

    # ========================================================================
    # TARIFF CONFIGURATIONS & TAXONOMY
    # ========================================================================

    seat_type = models.CharField(
        max_length=30,
        choices=SEAT_TYPE_CHOICES,
        default="SEAT",
        db_index=True,
        help_text="The layout material or tier category mapping this fare rate (e.g., SEAT, SLEEPER)",
    )

    price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="The official adult standard ticket base pricing scalar value",
    )

    child_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Concessionary ticket price explicitly allocated for child or minor passengers",
    )

    # ========================================================================
    # TIMELINE VALIDATION MATRIX
    # ========================================================================

    valid_from = models.DateField(
        help_text="The activation date from which this fare tariff becomes effective and open for bookings"
    )

    valid_to = models.DateField(
        null=True,
        blank=True,
        help_text="The closure date when this fare tariff structure ceases to be active (Null implies indefinite)",
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Designates whether this specific pricing line is actively considered by the ticketing engine",
    )

    class Meta:
        db_table = "trip_prices"
        verbose_name = _("Trip Price Tariff")
        verbose_name_plural = _("Trip Price Tariffs")
        ordering = ["tenant", "route", "seat_type", "-valid_from"]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Compound index optimized for high-velocity queries driving the consumer ticketing search engine
            models.Index(
                fields=["route", "seat_type", "is_active"],
                name="idx_price_booking_lookup",
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.route.name} [{self.seat_type}]: {self.price:,.0f} VND"

    # ========================================================================
    # BUSINESS LOGIC & COMPLIANCE VERIFICATION METHODS
    # ========================================================================

    def clean(self):
        """
        Application-layer validation checking matrix sanity and date boundaries prior to commits.
        """
        super().clean()

        # Financial validation rules
        if self.price and self.price < 0:
            raise ValidationError(
                {
                    "price": _(
                        "The base standard adult price cannot be a negative scalar value."
                    )
                }
            )

        if self.child_price and self.child_price < 0:
            raise ValidationError(
                {
                    "child_price": _(
                        "The concessionary child price cannot be a negative scalar value."
                    )
                }
            )

        if self.price and self.child_price and self.child_price > self.price:
            raise ValidationError(
                {
                    "child_price": _(
                        "Business Compliance Alert: Child concessionary price cannot exceed adult base pricing."
                    )
                }
            )

        # Seasonal calendar validation rules
        if self.valid_from and self.valid_to:
            if self.valid_from > self.valid_to:
                raise ValidationError(
                    {
                        "valid_to": _(
                            "The valid expiration date boundary cannot precede its effective activation date."
                        )
                    }
                )

    def get_applicable_price_by_age(self, is_child=False):
        """
        Helper method returning the matching fare dependent on the customer age metric.
        Fallbacks to default adult price if child tariff isn't explicitly configured.

        Args:
            is_child: Boolean

        Returns:
            Decimal (Target fare value)
        """
        if is_child and self.child_price is not None:
            return self.child_price
        return self.price

    # ========================================================================
    # CLASSMETHODS / TICKETING ENGINE DATA PIPELINES
    # ========================================================================

    @classmethod
    def get_active_tariff(cls, tenant_id, route_id, seat_type, target_date):
        """
        Fetch the exact applicable pricing tariff rule for a specific route matching a target date context.
        Highly critical method utilized inside live checkout carts and passenger reservation flows.

        Args:
            tenant_id: Integer
            route_id: Integer
            seat_type: String ('SEAT', 'SLEEPER', etc.)
            target_date: Date object (e.g., datetime.date)

        Returns:
            TripPrice model instance or None
        """
        return (
            cls.objects.filter(
                tenant_id=tenant_id,
                route_id=route_id,
                seat_type=seat_type,
                is_active=True,
                valid_from__lte=target_date,
            )
            .filter(
                models.Q(valid_to__isnull=True) | models.Q(valid_to__gte=target_date)
            )
            .order_by("-valid_from")
            .first()
        )  # Grabs the most specific/recently activated tariff if overlapping rules exist
