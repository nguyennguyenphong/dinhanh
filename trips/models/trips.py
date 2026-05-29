# ============================================================================
# FILE: apps/routes/models.py
# Trips Lifecycle Management Models
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db.models import Q

# Assuming these models exist in your production architecture
from tenants.models.tenants import Tenant
from routes.models.routes import Route
from trips.models.trip_schedules import TripSchedule
from vehicles.models.vehicles import Vehicle
from vehicles.models.seat_maps import SeatMap
from branches.models.branches import Branch


class Trip(models.Model):
    """
    Trip model representing an active operational journey executed on a specific calendar timeline.
    
    Features:
    - Multi-tenancy: Securely partitioned via tenant_id
    - Dynamic Assignment: Binds specific physical physical assets (Vehicle, SeatMap) to a route instance
    - Precise Chronology: Leverages timezone-aware fields (TIMESTAMPTZ) for all schedule & actual logs
    - Unique Code Identifier: Unique alphanumeric code enforced per tenant scope
    - Data Integrity: Database-level CHECK constraints guarding the operational lifecycle steps
    
    Statuses:
    - SCHEDULED: Planned journey, open for bookings/ticketing, asset allocated
    - BOARDING: Vehicle parked at platform, check-in gate active, welcoming passengers
    - DEPARTED: Left the origin terminal node, active on road transit line
    - ARRIVED: Successfully docked at final destination station, journey completed
    - CANCELLED: Aborted prior to departure with explicit text reason logging
    - DELAYED: Shifted beyond standard acceptable buffer thresholds from scheduled departure
    - DIVERTED: Route altered mid-transit due to severe weather, road blocks, or emergencies
    
    Example:
        # Create an active trip instance
        trip = Trip.objects.create(
            tenant_id=1,
            code='TRIP-20260530-001',
            route_id=4,
            departure_time='2026-05-30T05:00:00+07:00',
            estimated_arrival='2026-05-30T11:30:00+07:00',
            status='SCHEDULED'
        )
    """

    STATUS_CHOICES = (
        ('SCHEDULED', _('Scheduled - Planned upcoming journey')),
        ('BOARDING', _('Boarding - Welcome gates open at terminal')),
        ('DEPARTED', _('Departed - En-route active on highway')),
        ('ARRIVED', _('Arrived - Docked at terminal destination')),
        ('CANCELLED', _('Cancelled - Aborted operation line')),
        ('DELAYED', _('Delayed - Postponed timing window')),
        ('DIVERTED', _('Diverted - Transiting via alternative bypass')),
    )

    id = models.BigAutoField(primary_key=True)
    
    # ========================================================================
    # RELATIONSHIPS & MULTI-TENANCY
    # ========================================================================
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,  # Matches ON DELETE CASCADE from requirement
        default=1,
        related_name='trips',
        db_index=True,
        help_text='Tenant owner of this active operational trip journey',
        db_comment='Multi-tenancy tenant reference'
    )
    
    schedule = models.ForeignKey(
        TripSchedule,
        on_delete=models.SET_NULL,  # Matches ON DELETE SET NULL from requirement
        related_name='trips',
        null=True,
        blank=True,
        db_index=True,
        help_text='Reference to parent timetable blueprint configuration template if auto-generated',
        db_comment='Soft reference to originating timetable template'
    )
    
    route = models.ForeignKey(
        Route,
        on_delete=models.PROTECT,  # Production safety: lock route deletion if commercial trips are attached
        related_name='trips',
        db_index=True,
        help_text='The active physical transportation route corridor assigned to this trip',
        db_comment='Reference to structural track core'
    )
    
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,  # Matches ON DELETE SET NULL from requirement
        related_name='trips',
        null=True,
        blank=True,
        db_index=True,
        help_text='The physical commercial fleet asset deployed to execute this journey',
        db_comment='Reference to deployed mechanical fleet asset'
    )
    
    seat_map = models.ForeignKey(
        SeatMap,
        on_delete=models.SET_NULL,  # Matches ON DELETE SET NULL from requirement
        related_name='trips',
        null=True,
        blank=True,
        help_text='The configuration matrix snapshot blueprint determining layout inventory allocation',
        db_comment='Reference to structural layout map blueprint'
    )
    
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,  # Matches ON DELETE SET NULL from requirement
        related_name='trips',
        null=True,
        blank=True,
        db_index=True,
        help_text='The dispatch managing branch station hub holding tracking accountability',
        db_comment='Reference to supervising branch node'
    )
    
    # ========================================================================
    # TRIP CORE CODE IDENTITY
    # ========================================================================
    
    code = models.CharField(
        max_length=30,
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9\-_]+$',
                message='Code must contain only uppercase letters, numbers, hyphens, and underscores'
            )
        ],
        help_text='Unique commercial business code matching ticketing indexes (e.g., HAN-SGN-20260530-01)',
        db_comment='Unique system commercial transaction lookup token code'
    )
    
    # ========================================================================
    # TIME SPATIAL MATRIX (TIMEZONE-AWARE TIMESTAMPS)
    # ========================================================================
    
    departure_time = models.DateTimeField(
        db_index=True,
        help_text='The official planned/scheduled calendar date and time for departure gate release',
        db_comment='Planned departure timezone-aware timeline point'
    )
    
    estimated_arrival = models.DateTimeField(
        null=True,
        blank=True,
        help_text='The calculated estimated date and time for terminal destination arrival logs',
        db_comment='Estimated arrival timezone-aware timeline point'
    )
    
    actual_departure = models.DateTimeField(
        null=True,
        blank=True,
        help_text='The exact physical timestamp logged when wheel rotation began past terminal gates',
        db_comment='Real departure execution record timestamp'
    )
    
    actual_arrival = models.DateTimeField(
        null=True,
        blank=True,
        help_text='The exact physical timestamp logged when the asset successfully safely docked at destination terminal',
        db_comment='Real arrival execution record timestamp'
    )
    
    # ========================================================================
    # LIFECYCLE MONITORING & CONTROLS
    # ========================================================================
    
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='SCHEDULED',
        db_index=True,
        help_text='The core operational stage representing current journey lifecycle status',
        db_comment='Workflow progression taxonomy status string token'
    )
    
    cancel_reason = models.TextField(
        null=True,
        blank=True,
        help_text='Explicit legal/operational annotation stating why a scheduled line was aborted',
        db_comment='Cancellation background context logs'
    )
    
    delay_reason = models.TextField(
        null=True,
        blank=True,
        help_text='Context annotations explaining schedule drift variables (e.g., highway congestion, tire repairs)',
        db_comment='Timing delay background context logs'
    )
    
    notes = models.TextField(
        null=True,
        blank=True,
        help_text='Miscellaneous operational dispatcher logging data sheets, special alerts, or crew notes',
        db_comment='Administrative text log annotations'
    )
    
    # ========================================================================
    # SYSTEM AUDITS
    # ========================================================================
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp when this live commercial journey entity sheet was registered',
        db_comment='Creation timestamp'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp when parameters inside this trip profile sheet were last modified',
        db_comment='Last modification timestamp'
    )

    class Meta:
        db_table = 'trips'
        verbose_name = _('Trip')
        verbose_name_plural = _('Trips')
        ordering = ['departure_time', 'code']
        
        # ====================================================================
        # CONSTRAINTS
        # ====================================================================
        
        constraints = [
            # Unique commercial trip code per tenant scope (Matches UNIQUE (tenant_id, code))
            models.UniqueConstraint(
                fields=['tenant', 'code'],
                name='unique_tenant_trip_code'
            ),
            # Direct database-level CHECK constraint for absolute state sequence safety
            models.CheckConstraint(
                check=models.Q(status__in=[
                    'SCHEDULED', 'BOARDING', 'DEPARTED', 'ARRIVED', 'CANCELLED', 'DELAYED', 'DIVERTED'
                ]),
                name='chk_trip_status'
            )
        ]
        
        # ====================================================================
        # INDEXES
        # ====================================================================
        
        indexes = [
            # Multi-column index optimizing high-velocity queries driving customer-facing reservation searches
            models.Index(
                fields=['route', 'status', 'departure_time'],
                name='idx_trip_customer_search',
                db_comment='Optimize routing queries for active booking applications'
            ),
            # Index optimized for GPS monitoring boards or tracking pipelines checking active road nodes
            models.Index(
                fields=['vehicle', 'status'],
                name='idx_trip_fleet_active_tracking',
                db_comment='Optimize fleet dispatcher board lookup speed'
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"[{self.code}] {self.route.name} ({self.departure_time.strftime('%Y-%m-%d %H:%M')}) -> {self.status}"

    # ========================================================================
    # BUSINESS LOGIC & STATE TRANSLATION MONITORING METHODS
    # ========================================================================

    def clean(self):
        """
        Application-layer validation checking chronological sanity parameters prior to commits.
        """
        super().clean()
        
        # Chronological sequencing logic validation rules
        if self.departure_time and self.estimated_arrival:
            if self.departure_time > self.estimated_arrival:
                raise ValidationError({
                    'estimated_arrival': _('The estimated arrival marker cannot stand behind departure timelines.')
                })
                
        if self.actual_departure and self.actual_arrival:
            if self.actual_departure > self.actual_arrival:
                raise ValidationError({
                    'actual_arrival': _('Actual arrival execution timestamps cannot precede actual departure markers.')
                })

        # Structural data constraint validations mirroring status requirements
        if self.status == 'CANCELLED' and not self.cancel_reason:
            raise ValidationError({
                'cancel_reason': _('Aborting an open commercial trip requires an explicit structural cancellation log.')
            })
            
        if self.status == 'DELAYED' and not self.delay_reason:
            raise ValidationError({
                'delay_reason': _('Flagging a schedule line as delayed requires explaining root context background variables.')
            })

    def transition_to_departed(self):
        """
        Execute workflow state update moving the active line state to DEPARTED.
        Synchronizes operational telemetry data and pushes updates down to fleet assets.
        """
        from django.utils import timezone
        if self.status not in ['SCHEDULED', 'BOARDING', 'DELAYED']:
            raise ValidationError(_("Chrono workflow rule block: Only upcoming trips can transition to DEPARTED state."))
            
        self.status = 'DEPARTED'
        self.actual_departure = timezone.now()
        self.save(update_fields=['status', 'actual_departure', 'updated_at'])
        
        # Integration cascade link: Update vehicle fleet profile status immediately to context RUNNING
        if self.vehicle:
            self.vehicle.status = 'RUNNING'
            self.vehicle.save(update_fields=['status', 'updated_at'])

    def transition_to_arrived(self):
        """
        Execute final completion workflow. Closes out tracking states and releases vehicle blockages.
        """
        from django.utils import timezone
        if self.status != 'DEPARTED':
            raise ValidationError(_("Chrono workflow rule block: Journeys can only mark arrival from active DEPARTED/DIVERTED lines."))
            
        self.status = 'ARRIVED'
        self.actual_arrival = timezone.now()
        self.save(update_fields=['status', 'actual_arrival', 'updated_at'])
        
        # Integration cascade link: Release vehicle fleet back into AVAILABLE inventory pool slots
        if self.vehicle:
            self.vehicle.status = 'AVAILABLE'
            self.vehicle.save(update_fields=['status', 'updated_at'])