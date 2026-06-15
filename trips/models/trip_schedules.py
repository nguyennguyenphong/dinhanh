# ============================================================================
# FILE: apps/routes/models.py
# Trip Schedules Management Models
# ============================================================================

from django.contrib.postgres.fields import (  # Production feature for PostgreSQL SMALLINT[]
    ArrayField,
)
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from safedelete.models import SOFT_DELETE_CASCADE, SafeDeleteModel


class TripSchedule(SafeDeleteModel):
    """
    TripSchedule model acting as the master blueprint configuration for recurring route timetables.

    Features:
    - Multi-tenancy: Isolated and partitioned securely via tenant_id
    - Unique Code Identifier: Unique alphanumeric code enforced per tenant scope
    - Day-Of-Week Array: Utilizes PostgreSQL ArrayField to map repeating weekly cycles (1=Mon to 7=Sun)
    - Seasonal Lifespan: Validates calendar date limits via valid_from and valid_to metrics
    - Target Blueprint Assignment: Soft-links default required VehicleCategory profiles

    Example:
        # Create a daily morning recurring blueprint schedule
        schedule = TripSchedule.objects.create(
            tenant_id=1,
            code='SCH-HAN-SGN-0500',
            route_id=4,
            departure_time='05:00:00',
            arrival_time='11:30:00',
            days_of_week=[1, 2, 3, 4, 5],  # Weekdays only (Monday to Friday)
            category=sleeper_bus_category,
            valid_from='2026-01-01',
            valid_to='2026-12-31'
        )
    """

    _safedelete_policy = SOFT_DELETE_CASCADE

    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS & MULTI-TENANCY
    # ========================================================================

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        default=1,
        related_name="trip_schedules",
        db_index=True,
        help_text="Tenant owner of this recurring scheduling timetable blueprint",
    )

    route = models.ForeignKey(
        "routes.Route",
        on_delete=models.PROTECT,
        related_name="trip_schedules",
        db_index=True,
        help_text="The core spatial transportation route this schedule runs on",
    )

    category = models.ForeignKey(
        "vehicles.VehicleCategory",
        on_delete=models.SET_NULL,
        related_name="trip_schedules",
        null=True,
        blank=True,
        db_index=True,
        help_text="The recommended or required vehicle specification profile for this schedule allocation slot",
    )

    # ========================================================================
    # SCHEDULE IDENTITY & TIMETABLES
    # ========================================================================

    code = models.CharField(
        max_length=30,
        validators=[
            RegexValidator(
                regex=r"^[A-Z0-9\-_]+$",
                message="Code must contain only uppercase letters, numbers, hyphens, and underscores",
            )
        ],
        help_text="Unique business identification string code per tenant (e.g., FIX-HANOI-0600)",
    )

    departure_time = models.TimeField(
        help_text="The official clock time when a vehicle must leave the origin station"
    )

    arrival_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Estimated or planned clock time when the vehicle reaches the terminal hub",
    )

    # Native PostgreSQL array mapping: SMALLINT[] NOT NULL DEFAULT '{1,2,3,4,5,6,7}'
    days_of_week = ArrayField(
        models.PositiveSmallIntegerField(),
        default=list,
        help_text="Array of repeating weekday integer index trackers (1=Monday, 2=Tuesday, ..., 7=Sunday)",
    )

    # ========================================================================
    # LIFECYCLE CONTROLS & VALIDATION WINDOWS
    # ========================================================================

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Designates whether this timetable sequence is operational and actively generating daily trip records",
    )

    valid_from = models.DateField(
        null=True,
        blank=True,
        help_text="The calendar commencement date when this operational schedule becomes effective",
    )

    valid_to = models.DateField(
        null=True,
        blank=True,
        help_text="The calendar closing date when this operational schedule ceases to be valid",
    )

    # ========================================================================
    # SYSTEM AUDITS
    # ========================================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this timetable row master schema was registered",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when this timetable schema configurations were modified",
    )

    class Meta:
        db_table = "trip_schedules"
        verbose_name = _("Trip Schedule")
        verbose_name_plural = _("Trip Schedules")
        ordering = ["tenant", "route", "departure_time"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Enforces unique scheduling template code per tenant (Matches UNIQUE (tenant_id, code))
            models.UniqueConstraint(
                fields=["tenant", "code"], name="unique_tenant_trip_schedule_code"
            ),
        ]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Optimizes generation algorithms looking up schedules active for a specific seasonal range
            models.Index(
                fields=["is_active", "valid_from", "valid_to"],
                name="idx_sch_lifecycle_lookup",
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"[{self.code}] {self.route} @ {self.departure_time.strftime('%H:%M')}"

    # ========================================================================
    # BUSINESS LOGIC & AUTOMATION GENERATION HELPER METHODS
    # ========================================================================

    def clean(self):
        """
        Application-layer validation parsing strict constraints before saving to DB.
        """
        super().clean()

        # Handle array initialization defaults if saved via Django Forms/Admin empty
        if not self.days_of_week:
            self.days_of_week = [1, 2, 3, 4, 5, 6, 7]

        # Enforce that array integer indices fall strictly inside ISO calendar boundaries [1, 7]
        for day in self.days_of_week:
            if day < 1 or day > 7:
                raise ValidationError(
                    {
                        "days_of_week": _(
                            "Day index trackers must reside strictly within range limits 1 (Mon) and 7 (Sun)."
                        )
                    }
                )

        # Validate seasonal calendar overlaps sequence rules
        if self.valid_from and self.valid_to:
            if self.valid_from > self.valid_to:
                raise ValidationError(
                    {
                        "valid_to": _(
                            "The valid closure timeline date cannot precede its opening effective date."
                        )
                    }
                )

    def is_runnable_on_day(self, date_instance):
        """
        Verify if this schedule blueprint is structurally active for execution on a specific calendar date.
        Combines seasonal date window boundaries check with the recurring ISO day-of-week index.

        Args:
            date_instance: Date object (e.g., datetime.date)

        Returns:
            Boolean
        """
        if not self.is_active:
            return False

        # Check explicit seasonal constraints
        if self.valid_from and date_instance < self.valid_from:
            return False
        if self.valid_to and date_instance > self.valid_to:
            return False

        # ISO weekday map: 1 = Monday, ..., 7 = Sunday
        iso_weekday = date_instance.isoweekday()
        return iso_weekday in self.days_of_week

    # ========================================================================
    # CLASSMETHODS / ROSTER GENERATION DATA PIPELINES
    # ========================================================================

    @classmethod
    def get_active_blueprints_for_generation(cls, tenant_id, target_date):
        """
        Fetch all active schedules eligible to forge trips on a designated target processing date.
        Highly critical method utilized inside automated batch background generation jobs (Celery/Cron).

        Args:
            tenant_id: Integer
            target_date: Date object

        Returns:
            List of TripSchedule model instances matching criteria
        """
        # Phase 1: Filter broad candidate schemas down via composite DB indexing boundaries
        candidates = (
            cls.objects.filter(tenant_id=tenant_id, is_active=True)
            .filter(Q(valid_from__isnull=True) | Q(valid_from__lte=target_date))
            .filter(Q(valid_to__isnull=True) | Q(valid_to__gte=target_date))
            .select_related("route", "category")
        )

        # Phase 2: Refine via exact array index matching rules
        return [sch for sch in candidates if sch.is_runnable_on_day(target_date)]
