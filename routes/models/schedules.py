from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel


class Schedule(BaseModel):
    """
    Schedule model for route schedules

    Features:
    - Route assignment
    - Departure and arrival times
    - Capacity management
    - Status tracking

    Example:
        # Create schedule
        schedule = Schedule.objects.create(
            route=route,
            departure_time=time(08, 0),
            arrival_time=time(20, 0),
            capacity=50
        )
    """

    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    route = models.ForeignKey(
        "routes.Route",
        on_delete=models.CASCADE,
        related_name="schedules",
        db_index=True,
        help_text="Route for this schedule",
    )

    # ========================================================================
    # TIMING
    # ========================================================================

    departure_time = models.TimeField(help_text="Departure time")

    arrival_time = models.TimeField(help_text="Arrival time")

    # ========================================================================
    # CAPACITY
    # ========================================================================

    capacity = models.IntegerField(default=50, help_text="Vehicle capacity")

    # ========================================================================
    # STATUS
    # ========================================================================

    is_active = models.BooleanField(
        default=True, db_index=True, help_text="Schedule is active"
    )

    class Meta:
        db_table = "schedules"
        verbose_name = _("Schedule")
        verbose_name_plural = _("Schedules")
        ordering = ["route", "departure_time"]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Index for route queries
            models.Index(fields=["route"], name="idx_schedule_route"),
            # Index for time queries
            models.Index(fields=["departure_time"], name="idx_schedule_departure"),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.route.name} - {self.departure_time} to {self.arrival_time}"
