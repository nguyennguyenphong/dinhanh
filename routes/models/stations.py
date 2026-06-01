# ============================================================================
# FILE: apps/stations/models.py
# Station Models with Routes and Services
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db.models import Q, F
from routes.models.provinces import Province


class Station(models.Model):
    """
    Station model for transportation hubs

    Features:
    - Multi-province support: Stations across provinces
    - Coordinates: GPS location tracking
    - Contact information: Phone and address
    - Active status: Control station availability
    - Route management: Manage routes from station
    - Service tracking: Track services at station
    - Statistics: Monitor station usage
    - Audit trail: Track creation and updates

    Use Cases:
    - Bus stations
    - Train stations
    - Pickup points
    - Delivery hubs
    - Service centers
    - Distribution centers

    Example:
        # Create station
        station = Station.objects.create(
            code='HN_MAIN',
            name='Hanoi Main Station',
            province=province,
            address='123 Main St, Hanoi',
            latitude=21.0285,
            longitude=105.8542,
            phone='+84-24-1234-5678'
        )

        # Get routes
        routes = station.get_routes()

        # Get statistics
        stats = station.get_statistics()
    """

    id = models.AutoField(primary_key=True)

    # ========================================================================
    # STATION IDENTIFICATION
    # ========================================================================

    code = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[A-Z0-9_]+$",
                message="Code must contain only uppercase letters, numbers, and underscores",
            )
        ],
        help_text="Unique station code (e.g., HN_MAIN, SGN_WEST)",
    )

    name = models.CharField(max_length=255, help_text="Station name")

    # ========================================================================
    # LOCATION INFORMATION
    # ========================================================================

    province = models.ForeignKey(
        Province,
        on_delete=models.CASCADE,
        related_name="stations",
        db_index=True,
        help_text="Province where station is located",
    )

    address = models.TextField(
        null=True, blank=True, help_text="Full address of station"
    )

    # ========================================================================
    # COORDINATES
    # ========================================================================

    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="Latitude coordinate",
    )

    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="Longitude coordinate",
    )

    # ========================================================================
    # CONTACT INFORMATION
    # ========================================================================

    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^\+?[0-9\-\(\)\s]+$", message="Invalid phone number format"
            )
        ],
        help_text="Station phone number",
    )

    # ========================================================================
    # STATUS
    # ========================================================================

    is_active = models.BooleanField(
        default=True, db_index=True, help_text="Station is active and operational"
    )

    # ========================================================================
    # TIMESTAMPS
    # ========================================================================

    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, help_text="When station was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True, help_text="When station was last updated"
    )

    class Meta:
        db_table = "stations"
        verbose_name = _("Station")
        verbose_name_plural = _("Stations")
        ordering = ["province", "name"]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Index for province queries
            models.Index(fields=["province"], name="idx_station_province"),
            # Index for active stations
            models.Index(fields=["is_active"], name="idx_station_active"),
            # Index for code lookup
            models.Index(fields=["code"], name="idx_station_code"),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.name} ({self.code})"

    def clean(self):
        """Validate station"""
        if self.latitude and self.longitude:
            # Validate coordinates
            if not (-90 <= float(self.latitude) <= 90):
                raise ValidationError("Latitude must be between -90 and 90")
            if not (-180 <= float(self.longitude) <= 180):
                raise ValidationError("Longitude must be between -180 and 180")

    def save(self, *args, **kwargs):
        """Override save to enforce business rules"""
        self.clean()
        super().save(*args, **kwargs)

    # ========================================================================
    # COORDINATE METHODS
    # ========================================================================

    def has_coordinates(self):
        """
        Check if station has coordinates

        Returns:
            Boolean

        Example:
            if station.has_coordinates():
                # Can calculate distance
        """
        return self.latitude is not None and self.longitude is not None

    def get_coordinates(self):
        """
        Get coordinates as tuple

        Returns:
            Tuple (latitude, longitude) or None

        Example:
            coords = station.get_coordinates()
        """
        if self.has_coordinates():
            return (float(self.latitude), float(self.longitude))
        return None

    def get_distance_to(self, other_station):
        """
        Calculate distance to another station (Haversine formula)

        Args:
            other_station: Station instance

        Returns:
            Float (distance in km) or None

        Example:
            distance = station.get_distance_to(other_station)
        """
        if not self.has_coordinates() or not other_station.has_coordinates():
            return None

        from math import radians, cos, sin, asin, sqrt

        lat1, lon1 = float(self.latitude), float(self.longitude)
        lat2, lon2 = float(other_station.latitude), float(other_station.longitude)

        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers

        return c * r

    # ========================================================================
    # ROUTE METHODS
    # ========================================================================

    def get_routes_from(self):
        """
        Get routes starting from this station

        Returns:
            QuerySet of Route objects

        Example:
            routes = station.get_routes_from()
        """
        return self.routes_from.filter(is_active=True).order_by("name")

    def get_routes_to(self):
        """
        Get routes ending at this station

        Returns:
            QuerySet of Route objects

        Example:
            routes = station.get_routes_to()
        """
        return self.routes_to.filter(is_active=True).order_by("name")

    def get_all_routes(self):
        """
        Get all routes involving this station

        Returns:
            QuerySet of Route objects

        Example:
            routes = station.get_all_routes()
        """
        from django.db.models import Q

        return Route.objects.filter(
            Q(origin=self) | Q(destination=self), is_active=True
        ).order_by("name")

    def get_route_count(self):
        """
        Get number of routes

        Returns:
            Integer

        Example:
            count = station.get_route_count()
        """
        from django.db.models import Q

        return Route.objects.filter(
            Q(origin=self) | Q(destination=self), is_active=True
        ).count()

    # ========================================================================
    # SCHEDULE METHODS
    # ========================================================================

    def get_schedules(self):
        """
        Get all schedules for this station

        Returns:
            QuerySet of Schedule objects

        Example:
            schedules = station.get_schedules()
        """
        from django.db.models import Q

        return Schedule.objects.filter(
            Q(route__origin=self) | Q(route__destination=self), is_active=True
        ).order_by("departure_time")

    def get_departures(self):
        """
        Get departure schedules from this station

        Returns:
            QuerySet of Schedule objects

        Example:
            departures = station.get_departures()
        """
        return Schedule.objects.filter(route__origin=self, is_active=True).order_by(
            "departure_time"
        )

    def get_arrivals(self):
        """
        Get arrival schedules at this station

        Returns:
            QuerySet of Schedule objects

        Example:
            arrivals = station.get_arrivals()
        """
        return Schedule.objects.filter(
            route__destination=self, is_active=True
        ).order_by("arrival_time")

    # ========================================================================
    # STATISTICS METHODS
    # ========================================================================

    def get_statistics(self):
        """
        Get station statistics

        Returns:
            Dictionary with statistics

        Example:
            stats = station.get_statistics()
            # Returns: {
            #     'routes': 15,
            #     'schedules': 45,
            #     'departures': 20,
            #     'arrivals': 25
            # }
        """
        from django.db.models import Q

        routes = Route.objects.filter(
            Q(origin=self) | Q(destination=self), is_active=True
        ).count()

        schedules = Schedule.objects.filter(
            Q(route__origin=self) | Q(route__destination=self), is_active=True
        ).count()

        departures = Schedule.objects.filter(route__origin=self, is_active=True).count()

        arrivals = Schedule.objects.filter(
            route__destination=self, is_active=True
        ).count()

        return {
            "routes": routes,
            "schedules": schedules,
            "departures": departures,
            "arrivals": arrivals,
        }

    # ========================================================================
    # QUERY METHODS
    # ========================================================================

    @classmethod
    def get_by_code(cls, code):
        """
        Get station by code

        Args:
            code: Station code

        Returns:
            Station instance or None

        Example:
            station = Station.get_by_code('HN_MAIN')
        """
        try:
            return cls.objects.get(code=code)
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_active_stations(cls, province=None):
        """
        Get active stations

        Args:
            province: Optional province filter

        Returns:
            QuerySet of Station objects

        Example:
            stations = Station.get_active_stations(province)
        """
        query = cls.objects.filter(is_active=True)

        if province:
            query = query.filter(province=province)

        return query.order_by("name")

    @classmethod
    def search_stations(cls, query, province=None):
        """
        Search stations by name or code

        Args:
            query: Search query
            province: Optional province filter

        Returns:
            QuerySet of Station objects

        Example:
            results = Station.search_stations('Main', province)
        """
        from django.db.models import Q

        search_query = Q(name__icontains=query) | Q(code__icontains=query)

        if province:
            return cls.objects.filter(search_query, province=province)

        return cls.objects.filter(search_query)

    @classmethod
    def get_nearby_stations(cls, latitude, longitude, radius_km=50):
        """
        Get stations within radius

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            radius_km: Search radius in kilometers

        Returns:
            List of tuples (Station, distance)

        Example:
            nearby = Station.get_nearby_stations(21.0285, 105.8542, 50)
        """
        from math import radians, cos, sin, asin, sqrt

        stations = cls.objects.filter(
            latitude__isnull=False, longitude__isnull=False, is_active=True
        )

        results = []
        lat1, lon1 = radians(float(latitude)), radians(float(longitude))

        for station in stations:
            lat2, lon2 = radians(float(station.latitude)), radians(
                float(station.longitude)
            )

            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * asin(sqrt(a))
            r = 6371
            distance = c * r

            if distance <= radius_km:
                results.append((station, distance))

        # Sort by distance
        results.sort(key=lambda x: x[1])
        return results
