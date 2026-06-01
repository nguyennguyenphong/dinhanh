# ============================================================================
# FILE: apps/telematics/models.py
# Fleet Telematics & Live GPS Tracking Models
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _


class TripTracking(models.Model):
    """
    TripTracking model managing high-velocity GPS telemetry streams from active transit fleet assets.

    WARNING: This model represents a Native PostgreSQL Range Partitioned Table.
    Due to Django ORM limitations regarding database partitioning structures,
    'managed = False' is enforced. Creation and lifecycle alterations of this table
    and its yearly sub-partitions are handled exclusively via custom migration raw SQL scripts.

    Features:
    - Partitioning: Segmented by range rules mapping the 'recorded_at' timeline (Yearly chunks)
    - High-Precision Geometrics: Captures numeric coordinate fields with sub-decimeter location accuracy
    - Telematics Payload: Tracks speed scales (km/h) alongside dynamic azimuth heading degrees
    - Event Taxonomy: Classifies standard telemetry frames against exceptional roadside breakdown nodes

    Event Types:
    - LOCATION: Standard periodic background ping reporting active telemetry positioning coordinates
    - STOP: Vehicle deceleration dropped to absolute zero, triggering temporary stop event logger
    - START: Vehicle initiated acceleration from a stationary rest position
    - BREAKDOWN: Engine hazard, tire puncture, or mechanical failure requiring immediate road rescue
    - ARRIVAL: Destination terminal geofence reached, closing journey log
    """

    EVENT_TYPE_CHOICES = (
        ("LOCATION", _("Location - Periodic telematics telemetry ping")),
        ("STOP", _("Stop - Station or roadside stationary pause")),
        ("START", _("Start - Acceleration from stationary state")),
        ("BREAKDOWN", _("Breakdown - Mechanical or operational failure emergency")),
        ("ARRIVAL", _("Arrival - Geofence breach at final destination station")),
    )

    # Using BigAutoField matches BIGSERIAL primary key target requirements
    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    trip = models.ForeignKey(
        "trips.Trip",
        on_delete=models.CASCADE,  # Matches REFERENCES trips(id) ON DELETE CASCADE
        related_name="telemetry_logs",
        db_index=False,  # Enforcing False because we explicitly declare a composite index in the DB
        help_text="The active operational trip journey producing this telematics node frame",
    )

    # ========================================================================
    # GEOGRAPHIC COORDINATES & TELEMATICS PAYLOAD
    # ========================================================================

    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,  # Matches NUMERIC(10,7)
        help_text="High-precision GPS latitude coordinate parsed from the hardware device tracking module",
    )

    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,  # Matches NUMERIC(10,7)
        help_text="High-precision GPS longitude coordinate parsed from the hardware device tracking module",
    )

    speed_kmh = models.DecimalField(
        max_digits=6,
        decimal_places=2,  # Matches NUMERIC(6,2) supporting speeds up to 9999.99 km/h
        null=True,
        blank=True,
        help_text="Real-time velocity metric captured from vehicle OBD/GPS computing matrix units",
    )

    heading = models.DecimalField(
        max_digits=5,
        decimal_places=2,  # Matches NUMERIC(5,2) supporting compass azimuth bounds 0.00 to 360.00 degrees
        null=True,
        blank=True,
        help_text="Compass azimuth rotation angle in degrees indicating current transit direction vectors",
    )

    # ========================================================================
    # EVENT TAXONOMY & CHRONOLOGY
    # ========================================================================

    event_type = models.CharField(
        max_length=30,
        choices=EVENT_TYPE_CHOICES,
        null=True,
        blank=True,
        help_text="The classification token categorizing the behavioral status of the vehicle at this specific record node",
    )

    recorded_at = models.DateTimeField(
        help_text="Timezone-aware timestamp logging exactly when this telematics payload was written (Partition Routing Key)",
    )

    class Meta:
        db_table = "trip_tracking"
        verbose_name = _("Trip Tracking Telemetry Log")
        verbose_name_plural = _("Trip Tracking Telemetry Logs")
        ordering = ["-recorded_at"]

        # --------------------------------------------------------------------
        # CRITICAL PRODUCTION FLAG: Managed set to False bypasses standard auto-migrations.
        # This table layout is built manually via migrations.RunSQL scripts to structure range partitions.
        # --------------------------------------------------------------------
        managed = False

    def __str__(self):
        """String representation"""
        return f"Trip: {self.trip_id} @ {self.recorded_at.strftime('%Y-%m-%d %H:%M:%S')} - Speed: {self.speed_kmh or 0} km/h"
