# ============================================================================
# FILE: apps/routes/models.py
# Trip Staff Assignment Management Models
# ============================================================================

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class TripStaff(models.Model):
    """
    TripStaff model managing the crew assignment and roster matrix for individual commercial journeys.

    Features:
    - Many-to-Many with Metadata: Bridges Trips and Employees with operational role details
    - Fleet Role Taxonomy: Distinguishes primary operators from operational assistants and inspectors
    - Confirmation Workflow: Flags whether the assigned employee has acknowledged the dispatch command
    - Unique Constraint: Prevents duplicate allocations of the same employee onto a single trip node

    Roles:
    - DRIVER: Physical commercial vehicle operator (Main driver or co-driver)
    - ASSISTANT: Trip conductor, ticketing collector crew, or customer care staff on board
    - INSPECTOR: Internal ticket audit official or road compliance safety auditor

    Example:
        # Assign a driver to a commercial trip journey
        crew_assignment = TripStaff.objects.create(
            trip=trip_instance,
            employee=driver_employee_instance,
            role='DRIVER',
            shift_type=shift_type_instance,
            confirmed=False
        )
    """

    ROLE_CHOICES = (
        ("DRIVER", _("Driver - Fleet steering operator")),
        ("ASSISTANT", _("Assistant - Trip conductor crew")),
        ("INSPECTOR", _("Inspector - Compliance ticket auditor")),
    )

    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    trip = models.ForeignKey(
        "trips.Trip",
        on_delete=models.CASCADE,  # Matches ON DELETE CASCADE from requirement
        related_name="crew_assignments",
        db_index=True,
        help_text="The active commercial trip journey asset target mapping",
    )

    employee = models.ForeignKey(
        "hr.Employee",
        on_delete=models.PROTECT,  # Production safety: lock employee deletion if active trip logs depend on them
        related_name="trip_assignments",
        db_index=True,
        help_text="The staff member assigned to the trip crew panel",
    )

    shift_type = models.ForeignKey(
        "hr.ShiftType",
        on_delete=models.SET_NULL,  # Matches ON DELETE SET NULL from requirement
        related_name="trip_crew_shifts",
        null=True,
        blank=True,
        db_index=True,
        help_text="The specific daily working shift boundary profile covering this assignment time matrix",
    )

    # ========================================================================
    # ASSIGNMENT CONFIGURATIONS & STATUSES
    # ========================================================================

    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        db_index=True,
        help_text="The functional deployment role designated to this staff member inside the vehicle",
    )

    confirmed = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Designates whether the employee has acknowledged and accepted this flight/trip dispatch roster order",
    )

    class Meta:
        db_table = "trip_staff"
        verbose_name = _("Trip Staff Assignment")
        verbose_name_plural = _("Trip Staff Assignments")
        ordering = ["trip", "role", "employee"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Enforces exactly one assignment record per employee per trip (Matches UNIQUE (trip_id, employee_id))
            models.UniqueConstraint(
                fields=["trip", "employee"], name="unique_trip_employee_assignment"
            ),
        ]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Optimizes notifications and driver portal dashboards checking pending assignments
            models.Index(
                fields=["employee", "confirmed"],
                name="idx_staff_pending_rosters",
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.trip.code} - {self.role}: {self.employee.full_name} ({'Confirmed' if self.confirmed else 'Pending'})"

    # ========================================================================
    # ROSTER LOGIC & RISK VERIFICATION METHODS
    # ========================================================================

    def clean(self):
        """
        Application-layer integrity checks to block illegal operational rosters.
        """
        super().clean()

        # Cross-validation: Ensure a driver position employee is not assigned as an inspector, etc.
        if self.role == "DRIVER" and not self.employee.is_driver():
            raise ValidationError(
                {
                    "employee": _(
                        "The selected personnel cannot act as a DRIVER due to missing position qualifications."
                    )
                }
            )

        # Compliance Check: Ensure the driver does not have an expired commercial driving license
        if self.role == "DRIVER" and self.employee.has_expired_license():
            raise ValidationError(
                {
                    "employee": _(
                        "Safety Compliance Block: This driver holds an expired commercial vehicle driving license."
                    )
                }
            )

    def accept_dispatch_order(self):
        """
        Safely update confirmation flags driven by mobile application/driver portals.
        """
        if self.confirmed:
            return

        self.confirmed = True
        self.save(update_fields=["confirmed"])

        # Integration cascade hook point: Push real-time telematics signals
        # out to bến bãi monitoring nodes indicating crew readiness.

    # ========================================================================
    # CLASSMETHODS / DATA PIPELINES ANALYSIS
    # ========================================================================

    @classmethod
    def get_trip_crew_manifest(cls, trip_id):
        """
        Fetch the entire optimized operational crew roster mapped under a single commercial trip.

        Args:
            trip_id: Integer

        Returns:
            QuerySet of TripStaff objects with prefetched personnel metrics
        """
        return (
            cls.objects.filter(trip_id=trip_id)
            .select_related("employee", "shift_type")
            .order_by("role")
        )
