# ============================================================================
# FILE: apps/routes/models.py
# Route Management Models
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.db.models import Q

# Assuming these models exist in your production architecture
from tenants.models.tenants import Tenant
from routes.models.stations import Station


class Route(models.Model):
    """
    Route model for managing transportation paths between stations per tenant.

    Features:
    - Multi-tenancy: Isolated by tenant_id
    - Unique Constraint: Code must be unique within a tenant
    - Geo-routing: Connects origin and destination stations
    - Metrics: Metrics for distance (km) and estimated duration (minutes)
    - Query Optimization: Production-grade database indexing for high performance

    Example:
        # Create a route
        route = Route.objects.create(
            tenant_id=1,
            code='HN-SGN-01',
            name='Hanoi to Ho Chi Minh Express',
            origin=hn_station,
            destination=sgn_station,
            distance_km=1720.50,
            duration_min=120
        )

        # Get active routes for a tenant
        active_routes = Route.get_active_by_tenant(tenant_id=1)
    """

    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS (MULTI-TENANCY & STATIONS)
    # ========================================================================

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        default=1,
        related_name="routes",
        db_index=True,
        help_text="Tenant owner of this route",
    )

    origin = models.ForeignKey(
        Station,
        on_delete=models.RESTRICT,  # Production safety: prevent accidental station deletion
        related_name="origin_routes",
        db_index=True,
        help_text="Starting station of the route",
    )

    destination = models.ForeignKey(
        Station,
        on_delete=models.RESTRICT,  # Production safety: prevent accidental station deletion
        related_name="destination_routes",
        db_index=True,
        help_text="Ending station of the route",
    )

    # ========================================================================
    # ROUTE IDENTIFICATION
    # ========================================================================

    code = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r"^[A-Z0-9\-_]+$",
                message="Code must contain only uppercase letters, numbers, hyphens, and underscores",
            )
        ],
        help_text="Unique route code per tenant (e.g., HN-SGN-01)",
    )

    name = models.CharField(max_length=255, help_text="Descriptive name of the route")

    # ========================================================================
    # METRICS & STATUS
    # ========================================================================

    distance_km = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Route distance in kilometers",
    )

    duration_min = models.IntegerField(
        null=True, blank=True, help_text="Estimated travel duration in minutes"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Designates whether this route is active and operational",
    )

    # ========================================================================
    # TIMESTAMPS
    # ========================================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Timestamp when the route was created",
    )

    updated_at = models.DateTimeField(
        auto_now=True,  # Matches the update-on-modification intent of production
        help_text="Timestamp when the route was last updated",
    )

    class Meta:
        db_table = "routes"
        verbose_name = _("Route")
        verbose_name_plural = _("Routes")
        ordering = ["tenant", "code"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Unique code per tenant (Matches UNIQUE (tenant_id, code))
            models.UniqueConstraint(
                fields=["tenant", "code"], name="unique_tenant_route_code"
            ),
        ]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Index for performance filtering on active tenant routes
            models.Index(
                fields=["tenant", "is_active"], name="idx_route_tenant_active"
            ),
            # Index for performance filtering on specific paths
            models.Index(fields=["origin", "destination"], name="idx_route_path"),
        ]

    def __str__(self):
        """String representation"""
        return f"[{self.code}] {self.name}"

    # ========================================================================
    # BUSINESS LOGIC & UTILITY METHODS
    # ========================================================================

    def get_summary(self):
        """
        Get route summary info string.

        Returns:
            String

        Example:
            summary = route.get_summary()
            # Returns: "Hanoi -> Ho Chi Minh (1720.5 km, 120 mins)"
        """
        distance = f"{self.distance_km} km" if self.distance_km else "N/A"
        duration = f"{self.duration_min} mins" if self.duration_min else "N/A"
        return f"{self.origin.name} -> {self.destination.name} ({distance}, {duration})"

    def update_metrics(self, distance, duration):
        """
        Update route metrics safely.

        Args:
            distance: Decimal or Float (km)
            duration: Integer (minutes)

        Example:
            route.update_metrics(1500.25, 90)
        """
        self.distance_km = distance
        self.duration_min = duration
        self.save(update_fields=["distance_km", "duration_min", "updated_at"])

    # ========================================================================
    # CLASSMETHODS / QUERY METHODS
    # ========================================================================

    @classmethod
    def get_active_by_tenant(cls, tenant_id):
        """
        Get all active routes for a specific tenant.

        Args:
            tenant_id: Integer

        Returns:
            QuerySet of Route objects

        Example:
            routes = Route.get_active_by_tenant(1)
        """
        return cls.objects.filter(tenant_id=tenant_id, is_active=True).select_related(
            "origin", "destination"
        )

    @classmethod
    def search_routes(cls, tenant_id, query):
        """
        Search routes by code or name within a tenant scope.

        Args:
            tenant_id: Integer
            query: Search string

        Returns:
            QuerySet of Route objects

        Example:
            results = Route.search_routes(1, 'Express')
        """
        search_query = Q(code__icontains=query) | Q(name__icontains=query)
        return cls.objects.filter(search_query, tenant_id=tenant_id)
