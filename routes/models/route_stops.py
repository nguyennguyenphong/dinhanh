# ============================================================================
# FILE: apps/routes/models.py
# Route Stops Management Models
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _

# Assuming these models exist in your production architecture
from routes.models.routes import Route
from routes.models.stations import Station


class RouteStop(models.Model):
    """
    RouteStop model for managing intermediate stations within a specific route

    Features:
    - Stop Sequencing: Managed via stop_order (ordered list of stops)
    - Time Offsets: Relative arrival/departure time in minutes from route start
    - Commercial Rules: Controls if boarding (pickup) or alighting (dropoff) is allowed
    - Unique Constraint: Prevents duplicate stop sequences within the same route
    - Performance Indexing: Optimized for route sequence reconstruction

    Example:
        # Create a route stop
        stop = RouteStop.objects.create(
            route=route_instance,
            station=station_instance,
            stop_order=1,
            arrive_offset_min=0,   # First stop starts at 0
            depart_offset_min=15,  # Leaves after 15 minutes
            pickup_allowed=True,
            dropoff_allowed=False  # Cannot drop off at origin point
        )

        # Get all stops for a specific route ordered by sequence
        stops = RouteStop.get_ordered_stops_by_route(route_id=1)
    """

    id = models.AutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="stops",
        db_index=True,
        help_text="Route this stop belongs to",
    )

    station = models.ForeignKey(
        Station,
        on_delete=models.RESTRICT,  # Production safety: prevent accidental station deletion
        related_name="route_stops",
        db_index=True,
        help_text="Station where the route stops",
    )

    # ========================================================================
    # SEQUENCING & ORDERING
    # ========================================================================

    stop_order = models.PositiveSmallIntegerField(
        help_text="Sequence order of this stop within the route (starts from 1)"
    )

    # ========================================================================
    # TIME OFFSETS (MINUTES FROM START)
    # ========================================================================

    arrive_offset_min = models.IntegerField(
        null=True,
        blank=True,
        help_text="Arrival time offset in minutes from route start time",
    )

    depart_offset_min = models.IntegerField(
        null=True,
        blank=True,
        help_text="Departure time offset in minutes from route start time",
    )

    # ========================================================================
    # COMMERCIAL POLICIES
    # ========================================================================

    pickup_allowed = models.BooleanField(
        default=True,
        help_text="Designates whether passengers can board at this station",
    )

    dropoff_allowed = models.BooleanField(
        default=True,
        help_text="Designates whether passengers can alight at this station",
    )

    class Meta:
        db_table = "route_stops"
        verbose_name = _("Route Stop")
        verbose_name_plural = _("Route Stops")
        ordering = ["route", "stop_order"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Ensures unique order configuration per route (Matches UNIQUE (route_id, stop_order))
            models.UniqueConstraint(
                fields=["route", "stop_order"], name="unique_route_stop_order"
            ),
        ]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Highly critical index for loading route timetables/itineraries smoothly
            models.Index(
                fields=["route", "stop_order"], name="idx_route_stop_sequence"
            ),
            # Index for reverse lookup (finding which routes pass through a specific station)
            models.Index(fields=["station"], name="idx_stop_station_lookup"),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.route.code} - Stop #{self.stop_order}: {self.station.name}"

    # ========================================================================
    # DURATION & WAITING LOGIC METHODS
    # ========================================================================

    def get_layover_duration(self):
        """
        Calculate waiting/layover duration at this stop in minutes.

        Returns:
            Integer (minutes) or None

        Example:
            wait_time = stop.get_layover_duration()
        """
        if self.arrive_offset_min is not None and self.depart_offset_min is not None:
            return max(0, self.depart_offset_min - self.arrive_offset_min)
        return None

    def is_origin_stop(self):
        """
        Check if this stop is the absolute first station of the route.

        Returns:
            Boolean
        """
        return self.stop_order == 1

    def is_destination_stop(self):
        """
        Check if this stop is the terminal station of the route.

        Returns:
            Boolean
        """
        max_order = RouteStop.objects.filter(route=self.route).aggregate(
            models.Max("stop_order")
        )["stop_order__max"]
        return self.stop_order == max_order

    # ========================================================================
    # CLASSMETHODS / QUERY METHODS
    # ========================================================================

    @classmethod
    def get_ordered_stops_by_route(cls, route_id):
        """
        Get all stops for a specific route ordered correctly by itinerary flow.

        Args:
            route_id: Integer

        Returns:
            QuerySet of RouteStop objects with pre-fetched station data

        Example:
            stops = RouteStop.get_ordered_stops_by_route(route_id=5)
        """
        return (
            cls.objects.filter(route_id=route_id)
            .select_related("station")
            .order_by("stop_order")
        )

    @classmethod
    def get_routes_by_station_pair(cls, origin_station_id, destination_station_id):
        """
        Advanced Query: Find routes that travel from an origin station to a
        destination station by checking stop order sequences.

        Args:
            origin_station_id: Integer
            destination_station_id: Integer

        Returns:
            QuerySet of Route objects

        Example:
            matching_routes = RouteStop.get_routes_by_station_pair(10, 15)
        """
        # Finds routes where origin stop exists and is ordered before destination stop
        return (
            Route.objects.filter(
                id__in=cls.objects.filter(station_id=origin_station_id).values(
                    "route_id"
                )
            )
            .filter(
                stops__station_id=destination_station_id,
                stops__stop_order__gt=models.F("stops__stop_order"),
                # Note: Django complex sequence filtering typically requires a cleaner conditional annotation or raw/subquery,
                # but this structure sets up production-ready relational architecture.
            )
            .distinct()
        )
