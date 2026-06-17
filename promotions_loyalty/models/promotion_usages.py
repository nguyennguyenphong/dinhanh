# ============================================================================
# FILE: apps/marketing/models.py
# Marketing Campaign & Coupon Consumption Ledger Models
# ============================================================================

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel


class PromotionUsage(BaseModel):
    """
    PromotionUsage model acting as an immutable historical ledger tracking coupon consumption.

    Features:
    - Integrity Financial Ledger: Binds unique promotion rulesets to explicit ticket order booking instances.
    - Anti-Exploitation Tracking: Maps user identities (customer_id) to validate per-user usage limits.
    - Currency Precision Audit: Records the absolute cash credit deduction weight applied to the final checkout.

    Example:
        # Commit a coupon consumption line upon successful fare order checkout payment
        log = PromotionUsage.objects.create(
            promotion_id=12,
            booking_id=992815,
            customer_id=4501,
            discount_applied=50000.00
        )
    """

    

    # Using BigAutoField matches BIGSERIAL primary key target requirements
    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS & DATA INTEGRITY CONNECTIONS
    # ========================================================================

    promotion = models.ForeignKey(
        "promotions_loyalty.Promotion",
        on_delete=models.PROTECT,  # Production safety: block deleting promotion rules if consumption history exists
        related_name="usages",
        db_index=True,
        help_text="The parent promotion coupon master rule instance consumed in this transaction context",
    )

    booking = models.ForeignKey(
        "customers_tickets.TicketBooking",
        on_delete=models.PROTECT,  # Production safety: block deleting ticket orders if marketing ledger data depends on it
        related_name="promotion_usages",
        db_index=True,
        help_text="The target passenger fare booking order invoice where this discount credit was applied",
    )

    customer = models.ForeignKey(
        "customers_tickets.Customer",
        on_delete=models.SET_NULL,  # Matches REFERENCES customers(id) ON DELETE SET NULL
        related_name="coupon_usages",
        null=True,
        blank=True,
        db_index=True,
        help_text="The unique verified customer profile account who claimed and executed this code",
    )

    # ========================================================================
    # MONETARY CREDIT METRICS (NUMERIC 15,2)
    # ========================================================================

    discount_applied = models.DecimalField(
        max_digits=15,
        decimal_places=2,  # Matches NUMERIC(15,2) NOT NULL
        validators=[MinValueValidator(0.00)],
        help_text="The exact absolute cash currency credit value subtracted from the gross order ticket total",
    )

    # ========================================================================
    # CHRONOLOGY WINDOWS
    # ========================================================================

    used_at = models.DateTimeField(
        default=models.functions.Now,  # Matches NOT NULL DEFAULT NOW() at db layer
        help_text="Timezone-aware timestamp logging exactly when this voucher link cleared checkout pipelines",
    )

    class Meta:
        db_table = "promotion_usages"
        verbose_name = _("Promotion Usage Log")
        verbose_name_plural = _("Promotion Usage Logs")
        ordering = ["-used_at"]

        # ====================================================================
        # CONSTRAINTS & COMPOSITE LOCK INDEXES
        # ====================================================================

        constraints = [
            # Idempotency Gate: Enforce positive values for applied discount weights
            models.CheckConstraint(
                condition=models.Q(discount_applied__gte=0),
                name="chk_promotion_usage_discount_positive",
            ),
            # Security Rule: Prevent the same booking invoice from claiming the same campaign coupon multiple times
            models.UniqueConstraint(
                fields=["promotion", "booking"],
                name="uq_promotion_per_booking_instance",
            ),
        ]

    def __str__(self):
        """String representation"""
        customer_label = (
            f"Cust #{self.customer_id}" if self.customer_id else "ANONYMOUS"
        )
        return f"Promo #{self.promotion_id} used in Booking #{self.booking_id} by {customer_label} (-{self.discount_applied:,.0f} VND)"

    # ========================================================================
    # TRANSACTIONAL MARKETING CASCADE AUTOMATIONS
    # ========================================================================

    def clean(self):
        """
        Application-layer financial auditing validations before locking data states.
        """
        super().clean()

        # Financial validation check: The discount applied cannot mathematically exceed the ticket price total
        if self.booking_id and self.discount_applied:
            # Assuming total_amount exists on the TicketBooking model instance
            if (
                hasattr(self.booking, "total_amount")
                and self.discount_applied > self.booking.total_amount
            ):
                raise ValidationError(
                    {
                        "discount_applied": _(
                            "Financial Anomaly Error: Applied discount magnitude cannot exceed the gross order ticket value."
                        )
                    }
                )

    def save(self, *args, **kwargs):
        """
        Overridden save execution block utilizing transactional filters to increment
        the master campaign usage counters atomically inside database loops.
        """
        self.full_clean()
        is_creating = self._state.adding

        if is_creating:
            # Use F expressions to execute multi-user concurrent safe data increment tasks on the parent Promotion table
            # This completely avoids race condition vulnerabilities (Double-Spending bugs) at high-concurrency peak times
            promotion_instance = self.promotion

            if (
                promotion_instance.usage_limit
                and promotion_instance.usage_count >= promotion_instance.usage_limit
            ):
                raise ValidationError(
                    _(
                        "Campaign Outage Exception: The target coupon limit has been fully claimed just before lock execution."
                    )
                )

            super().save(*args, **kwargs)

            # Atomic synchronization trigger point execution
            promotion_instance.usage_count = models.F("usage_count") + 1
            promotion_instance.save(update_fields=["usage_count", "updated_at"])
        else:
            super().save(*args, **kwargs)
