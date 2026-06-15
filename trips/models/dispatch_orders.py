# ============================================================================
# FILE: apps/routes/models.py
# Fleet Dispatch Order Management Models
# ============================================================================

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from safedelete.models import SOFT_DELETE_CASCADE, SafeDeleteModel


class DispatchOrder(SafeDeleteModel):
    """
    DispatchOrder model acting as the official operational clearance certificate for a commercial trip.

    Features:
    - Strict 1-to-1 Mapping: Direct models.OneToOneField linkage with Trips (Matches UNIQUE and REFERENCES trips)
    - Pre-Departure Checklist: Utilizes JSONB field to verify mechanical, legal, and safety parameters
    - Dispatch Audit Sign-off: Tracks explicit authorization credentials (issued_by, issued_at)
    - Lifecycle Synchronization: Automatically alters parent Trip states during progression events

    Statuses:
    - PENDING: Document initialized, awaiting supervisor validation and checklist confirmation
    - ISSUED: Clearance approved by dispatcher, vehicle is cleared to activate boarding procedures
    - DEPARTED: Vehicle has officially breached terminal boundary gates and is active en-route

    Example:
        # Create a pending dispatch authorization document
        order = DispatchOrder.objects.create(
            trip=trip_instance,
            checklist={
                "brakes_verified": True,
                "driver_sober": True,
                "tires_pressure_ok": True,
                "legal_documents_on_board": True
            },
            status='PENDING'
        )
    """

    _safedelete_policy = SOFT_DELETE_CASCADE

    STATUS_CHOICES = (
        ("PENDING", _("Pending - Awaiting checklist validation and approval sign-off")),
        (
            "ISSUED",
            _("Issued - Dispatch cleared, vehicle ready for terminal departure"),
        ),
        ("DEPARTED", _("Departed - Vehicle passed exit gate, trip active en-route")),
    )

    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    trip = models.OneToOneField(
        "trips.Trip",
        on_delete=models.CASCADE,  # Matches NOT NULL UNIQUE REFERENCES trips(id) ON DELETE CASCADE
        related_name="dispatch_order",
        help_text="The unique commercial trip journey assigned under this dispatch directive paper",
    )

    issued_by = models.ForeignKey(
        "accounts.UserAccount",
        on_delete=models.SET_NULL,  # Matches REFERENCES user_accounts(id) ON DELETE SET NULL
        related_name="issued_dispatches",
        null=True,
        blank=True,
        db_index=True,
        help_text="The active dispatcher or station manager authorizing this departure clearance",
    )

    # ========================================================================
    # METADATA & COMPLIANCE CHECKLISTS
    # ========================================================================

    issued_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timezone-aware timestamp logging exactly when clearance approval was executed",
    )

    # Native PostgreSQL JSONB architecture integration
    checklist = models.JSONField(
        default=dict,
        help_text="Complex data matrix validating dynamic safe pre-departure parameters (e.g., fuel, brakes, safety)",
    )

    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Miscellaneous comments from the supervisor, delay flags, or terminal exceptional logs",
    )

    # ========================================================================
    # WORKFLOW PROGRESSION LIEFOCYCLES
    # ========================================================================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
        db_index=True,
        help_text="The progression state tracking this dispatch order within the gate house terminal ecosystem",
    )

    # ========================================================================
    # SYSTEM AUDITS
    # ========================================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this dispatch ledger paper line was first opened",
    )

    class Meta:
        db_table = "dispatch_orders"
        verbose_name = _("Dispatch Order")
        verbose_name_plural = _("Dispatch Orders")
        ordering = ["-created_at"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Direct database-level CHECK constraint for absolute state sequence safety
            models.CheckConstraint(
                condition=models.Q(status__in=["PENDING", "ISSUED", "DEPARTED"]),
                name="chk_dispatch_order_status",
            )
        ]

    def __str__(self):
        """String representation"""
        return f"DO-{self.id:06d} -> Trip: {self.trip.code} [{self.status}]"

    # ========================================================================
    # BUSINESS LOGIC & AUTOMATION PROCESS METHODS
    # ========================================================================

    def clean(self):
        """
        Application-layer validation checking compliance rules prior to state transitions.
        """
        super().clean()

        if self.status in ["ISSUED", "DEPARTED"] and not self.issued_by:
            raise ValidationError(
                {
                    "issued_by": _(
                        "Operational Compliance Alert: An order cannot transition to ISSUED/DEPARTED without an authorizing supervisor signature."
                    )
                }
            )

    def execute_clearance_release(self, supervisor_user):
        """
        Authorize the dispatch order, log the audit stamps, and move parent trip to BOARDING.

        Args:
            supervisor_user: UserAccount model instance
        """
        if self.status != "PENDING":
            raise ValidationError(
                _(
                    "This dispatch order document has already bypassed its reviewable PENDING state."
                )
            )

        from django.utils import timezone

        self.status = "ISSUED"
        self.issued_by = supervisor_user
        self.issued_at = timezone.now()
        self.save(update_fields=["status", "issued_by", "issued_at"])

        # Cascade Side-Effect: Automatically advance the attached trip into the BOARDING phase
        if self.trip.status == "SCHEDULED":
            self.trip.status = "BOARDING"
            self.trip.save(update_fields=["status", "updated_at"])

    def register_gate_departure(self):
        """
        Finalize order status when vehicle rolls past the physical gate house.
        Triggers the synchronized departure pipeline across fleet management nodes.
        """
        if self.status != "ISSUED":
            raise ValidationError(
                _(
                    "Gate House Error: Vehicle cannot pass exit gate without a verified ISSUED clearance certificate."
                )
            )

        self.status = "DEPARTED"
        self.save(update_fields=["status"])

        # Cascade Side-Effect: Core integration hook. Transition the trip to DEPARTED on highway networks
        self.trip.transition_to_departed()
