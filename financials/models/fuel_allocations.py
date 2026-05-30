# ============================================================================
# FILE: apps/fleet/models.py
# Fleet Management, Asset Fuel Allocations & Logistics Models
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

# Assuming these models exist in your production architecture
from vehicles.models.vehicles import Vehicle
from trips.models.trips import Trip
from hr.models.employees import Employee
from accounts.models.user_accounts import UserAccount  # Custom user model


class FuelAllocation(models.Model):
    """
    FuelAllocation model tracking physical fuel injections, pricing, and consumption logs per fleet vehicle.
    
    Features:
    - Automated Financial Derivation: Validates and auto-calculates gross totals mathematically to preserve ledger sync.
    - Anti-Fraud Odometer Logs: Snapshots odometer metrics to calculate fuel efficiency (km/liter) analytics down-stream.
    - Double-Anchor Logistics Tracking: Binds fuel expenses directly to a physical truck/bus and an active route trip node.
    - High-Performance Combined Indexing: Optimized for rapid chronological consumption queries per vehicular asset.
    
    Example:
        # Commit a verified diesel allocation receipt filled at a partner petrol station
        allocation = FuelAllocation.objects.create(
            vehicle_id=12,         # Bus plate 29B-12345
            trip_id=9810,          # Active Hanoi - Danang trip pipeline
            driver_id=402,         # Assigned fleet driver
            liters=150.00,         # 150 Liters filled
            price_per_liter=22500.00,
            station_name='Petrolimex Station No. 18',
            odometer=145230.50,
            allocated_by=1         # Dispensing dispatcher staff account
        )
    """

    id = models.AutoField(primary_key=True)
    
    # ========================================================================
    # RELATIONSHIPS & PHYSICAL ASSET DESTINATIONS
    # ========================================================================
    
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,  # Matches ON DELETE CASCADE from requirement
        related_name='fuel_allocations',
        db_index=True,
        help_text='The target fleet vehicle profile node receiving the physical fuel volume injection',
        db_comment='Cascade reference targeting primary fleet asset vehicle model'
    )
    
    trip = models.ForeignKey(
        Trip,
        on_delete=models.SET_NULL,  # Matches REFERENCES trips(id) ON DELETE SET NULL
        related_name='fuel_allocations',
        null=True,
        blank=True,
        db_index=True,
        help_text='The specific operational route journey execution segment where this fuel consumption is assigned',
        db_comment='Soft reference mapping operational trip document instance'
    )
    
    driver = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,  # Matches REFERENCES employees(id) ON DELETE SET NULL
        related_name='fuel_allocations',
        null=True,
        blank=True,
        db_index=True,
        help_text='The professional driver operational employee operating the vehicle at the timestamp of refueling',
        db_comment='Soft reference mapping corporate fleet operator employee profile'
    )
    
    allocated_by = models.ForeignKey(
        UserAccount,
        on_delete=models.SET_NULL,  # Matches REFERENCES user_accounts(id) ON DELETE SET NULL
        related_name='authorized_fuel_allocations',
        null=True,
        blank=True,
        db_index=True,
        help_text='The dispatcher clerk or internal back-office user logging or signing off this fuel ticket voucher',
        db_comment='Soft reference tracking authorizing supervisor user account'
    )
    
    # ========================================================================
    # QUANTITATIVE FUEL MATRICES & LOGISTICAL REGISTERS
    # ========================================================================
    
    liters = models.DecimalField(
        max_digits=8,
        decimal_places=2,  # Matches NUMERIC(8,2) NOT NULL
        validators=[MinValueValidator(0.01)],
        help_text='The volume of fuel pumped, measured precisely in liters',
        db_comment='Physical fuel liquid volume magnitude quantity in liters'
    )
    
    price_per_liter = models.DecimalField(
        max_digits=10,
        decimal_places=2,  # Matches NUMERIC(10,2) NOT NULL
        validators=[MinValueValidator(0.01)],
        help_text='The single unit market price weight per fuel liter at the timestamp of allocation (e.g., VND/Liter)',
        db_comment='Single unit fuel volume currency cost pricing scalar'
    )
    
    total_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,  # Matches NUMERIC(15,2) NOT NULL
        validators=[MinValueValidator(0.01)],
        help_text='The aggregate financial liability cash weight (liters multiplied by price_per_liter)',
        db_comment='Calculated absolute aggregate gross expenditure currency total cost'
    )
    
    station_name = models.CharField(
        max_length=255,  # Matches VARCHAR(255) nullable specifications
        null=True,
        blank=True,
        help_text='The physical commercial brand name or location metadata text of the gas pump station (e.g., PV OIL Branch 2)',
        db_comment='Commercial petrol supply station enterprise brand text'
    )
    
    odometer = models.DecimalField(
        max_digits=10,
        decimal_places=2,  # Matches NUMERIC(10,2) nullable specifications
        null=True,
        blank=True,
        validators=[MinValueValidator(0.00)],
        help_text='The absolute physical counter dashboard mileage meter reading snapshot at refueling checkpoint',
        db_comment='Vehicular structural counter dashboard mileage meter snapshot value'
    )
    
    # ========================================================================
    # CHRONOLOGY WINDOWS & METADATA LOGS
    # ========================================================================
    
    notes = models.TextField(
        null=True,
        blank=True,
        help_text='Granular operational explanations or unexpected incident logging data lines',
        db_comment='Administrative textual log annotations'
    )
    
    allocated_at = models.DateTimeField(
        default=models.functions.Now,  # Matches NOT NULL DEFAULT NOW() at DDL compilation layer
        help_text='Timezone-aware calendar timestamp tracking when the physical fuel was dispensed into the tank',
        db_comment='Physical fuel deployment execution timestamp'
    )
    
    created_at = models.DateTimeField(
        default=models.functions.Now,  # Matches NOT NULL DEFAULT NOW() at DDL core layer
        help_text='System log row registration initialization milestone timestamp',
        db_comment='Creation timestamp'
    )

    class Meta:
        db_table = 'fuel_allocations'
        verbose_name = _('Fuel Allocation Voucher')
        verbose_name_plural = _('Fuel Allocation Vouchers')
        
        # Matches down-stream query optimizations: Priority on latest fuel ticket rows per truck
        ordering = ['vehicle', '-allocated_at']
        
        # ====================================================================
        # HIGH-PERFORMANCE COMPOSITE PRODUCTION INDEXES & CONSTRAINTS
        # ====================================================================
        
        indexes = [
            # Replicates exact structure of: CREATE INDEX idx_fuel_vehicle ON fuel_allocations(vehicle_id, allocated_at DESC);
            # Critical optimization for fuel efficiency calculations monitoring consumption trends of a single bus/truck chronologically.
            models.Index(
                fields=['vehicle', '-allocated_at'],
                name='idx_fuel_vehicle'
            )
        ]
        
        constraints = [
            # Direct database-level validations: numeric fields cannot accept absolute zero or negative inputs
            models.CheckConstraint(
                check=models.Q(liters__gt=0) & models.Q(price_per_liter__gt=0) & models.Q(total_cost__gt=0),
                name='chk_fuel_metrics_strictly_positive'
            ),
            # Odometer constraint: dashboard metrics must possess reasonable values if registered
            models.CheckConstraint(
                check=models.Q(odometer__gte=0) | models.Q(odometer__isnull=True),
                name='chk_fuel_odometer_positive'
            )
        ]

    def __str__(self):
        """String representation"""
        return f"Fuel Allocation #{self.id} | Vehicle #{self.vehicle_id} (-{self.total_cost:,.0f} VND)"

    # ========================================================================
    # PRODUCTION FINANCIAL DERIVATION & ODOMETER VERIFICATION ENGINES
    # ========================================================================

    def clean(self):
        """
        Application-layer auditing matrix synchronizing numeric calculations and odometer validation.
        """
        super().clean()
        
        from decimal import Decimal
        
        # 1. Automating Financial Calculus & Integrity Synchronization
        if self.liters and self.price_per_liter:
            calculated_cost = Decimal(str(self.liters)) * Decimal(str(self.price_per_liter))
            
            if not self.total_cost:
                # Automate assignment if the developer/API leaves it out of payload dictionary arguments
                self.total_cost = calculated_cost
            else:
                # Verification Check: Block entries with math disparities between fields to prevent fraud
                if abs(Decimal(str(self.total_cost)) - calculated_cost) > Decimal('0.01'):
                    raise ValidationError({
                        'total_cost': _(f"Ledger Balance Deflection: Disparity detected. Mathematically expected total is {calculated_cost:,.2f} VND.")
                    })
                    
        # 2. Advanced Security Check: Historical Odometer Sequence Auditing
        if self.vehicle_id and self.odometer:
            # Query the latest sequential allocation record prior to this current timestamp
            latest_ticket = FuelAllocation.objects.filter(
                vehicle_id=self.vehicle_id,
                allocated_at__lt=self.allocated_at or models.functions.Now()
            ).order_by('-allocated_at').first()
            
            if latest_ticket and latest_ticket.odometer and self.odometer < latest_ticket.odometer:
                raise ValidationError({
                    'odometer': _(f"Anti-Fraud Sequence Fault: Current mileage ({self.odometer:,.2f} km) cannot mathematically sit lower than the last recorded entry ({latest_ticket.odometer:,.2f} km).")
                })

    def save(self, *args, **kwargs):
        """
        Overridden save execution forcing full validation execution sweeps before locking rows down into disk partitions.
        """
        self.full_clean()
        super().save(*args, **kwargs)