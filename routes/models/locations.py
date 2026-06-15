from django.db import models
from django.utils.translation import gettext_lazy as _
from safedelete.models import SOFT_DELETE_CASCADE, SafeDeleteModel


class Location(SafeDeleteModel):
    """
    Location model for specific addresses

    Features:
    - Ward relationship: Link to ward
    - Street address: Store street details
    - Coordinates: Store GPS coordinates
    - Location type: Classify location
    - Statistics: Track usage

    Location Types:
    - OFFICE: Office location
    - WAREHOUSE: Warehouse location
    - PICKUP: Pickup point
    - DELIVERY: Delivery point
    - BRANCH: Branch office
    - CUSTOM: Custom location

    Example:
        # Create location
        location = Location.objects.create(
            ward=ward,
            name='Main Office',
            address='123 Hang Trong St',
            location_type='OFFICE',
            latitude=21.0285,
            longitude=105.8542
        )

        # Get full address
        full_address = location.get_full_address()

        # Get distance to another location
        distance = location.get_distance_to(other_location)
    """

    _safedelete_policy = SOFT_DELETE_CASCADE

    LOCATION_TYPE_CHOICES = (
        ("OFFICE", _("Office - Office location")),
        ("WAREHOUSE", _("Warehouse - Warehouse location")),
        ("PICKUP", _("Pickup - Pickup point")),
        ("DELIVERY", _("Delivery - Delivery point")),
        ("BRANCH", _("Branch - Branch office")),
        ("CUSTOM", _("Custom - Custom location")),
    )

    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    ward = models.ForeignKey(
        "routes.Ward",
        on_delete=models.CASCADE,
        related_name="locations",
        db_index=True,
        help_text="Ward this location is in",
    )

    # ========================================================================
    # LOCATION INFORMATION
    # ========================================================================

    name = models.CharField(max_length=200, help_text="Location name")

    address = models.CharField(max_length=500, help_text="Street address")

    location_type = models.CharField(
        max_length=30,
        choices=LOCATION_TYPE_CHOICES,
        default="CUSTOM",
        db_index=True,
        help_text="Type of location",
    )

    # ========================================================================
    # COORDINATES
    # ========================================================================

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Latitude coordinate",
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Longitude coordinate",
    )

    # ========================================================================
    # TIMESTAMPS
    # ========================================================================

    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, help_text="When location was created"
    )

    class Meta:
        db_table = "locations"
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")
        ordering = ["ward", "name"]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Index for ward queries
            models.Index(fields=["ward"], name="idx_location_ward"),
            # Index for location type queries
            models.Index(fields=["location_type"], name="idx_location_type"),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.name} ({self.ward.name})"

    # ========================================================================
    # ADDRESS METHODS
    # ========================================================================

    def get_full_address(self):
        """
        Get full address with hierarchy

        Returns:
            String

        Example:
            full = location.get_full_address()
            # Returns: "123 Hang Trong St, Hang Trong, Hoan Kiem, Hanoi"
        """
        parts = [
            self.address,
            self.ward.name,
            self.ward.district.name,
            self.ward.district.province.name,
        ]
        return ", ".join(filter(None, parts))

    def get_short_address(self):
        """
        Get short address

        Returns:
            String

        Example:
            short = location.get_short_address()
            # Returns: "123 Hang Trong St, Hanoi"
        """
        return f"{self.address}, {self.ward.district.province.name}"

    def has_coordinates(self):
        """
        Check if location has coordinates

        Returns:
            Boolean

        Example:
            if location.has_coordinates():
                # Can calculate distance
        """
        return self.latitude is not None and self.longitude is not None

    def get_coordinates(self):
        """
        Get coordinates as tuple

        Returns:
            Tuple (latitude, longitude) or None

        Example:
            coords = location.get_coordinates()
        """
        if self.has_coordinates():
            return (float(self.latitude), float(self.longitude))
        return None

    def get_distance_to(self, other_location):
        """
        Calculate distance to another location (Haversine formula)

        Args:
            other_location: Location instance

        Returns:
            Float (distance in km) or None

        Example:
            distance = location.get_distance_to(other_location)
        """
        if not self.has_coordinates() or not other_location.has_coordinates():
            return None

        from math import asin, cos, radians, sin, sqrt

        lat1, lon1 = self.latitude, self.longitude
        lat2, lon2 = other_location.latitude, other_location.longitude

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
    # QUERY METHODS
    # ========================================================================

    @classmethod
    def get_by_province(cls, province):
        """
        Get all locations in province

        Args:
            province: Province instance

        Returns:
            QuerySet of Location objects

        Example:
            locations = Location.get_by_province(province)
        """
        return cls.objects.filter(ward__district__province=province).order_by(
            "ward__district", "ward", "name"
        )

    @classmethod
    def get_by_district(cls, district):
        """
        Get all locations in district

        Args:
            district: District instance

        Returns:
            QuerySet of Location objects

        Example:
            locations = Location.get_by_district(district)
        """
        return cls.objects.filter(ward__district=district).order_by("ward", "name")

    @classmethod
    def get_by_type(cls, location_type):
        """
        Get locations by type

        Args:
            location_type: Location type

        Returns:
            QuerySet of Location objects

        Example:
            offices = Location.get_by_type('OFFICE')
        """
        return cls.objects.filter(location_type=location_type).order_by(
            "ward__district__province", "name"
        )

    @classmethod
    def search_locations(cls, query, province=None):
        """
        Search locations by name or address

        Args:
            query: Search query
            province: Optional province filter

        Returns:
            QuerySet of Location objects

        Example:
            results = Location.search_locations('Main Office', province)
        """
        from django.db.models import Q

        search_query = Q(name__icontains=query) | Q(address__icontains=query)

        if province:
            return cls.objects.filter(search_query, ward__district__province=province)

        return cls.objects.filter(search_query)
