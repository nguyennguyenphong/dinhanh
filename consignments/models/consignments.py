# ============================================================================
# FILE: apps/logistics/models.py
# Cargo Logistics & Consignment Ledger Models
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinValueValidator
from django.db.models import Q

# Assuming these models exist in your production architecture
from tenants.models.tenants import Tenant
from trips.models.trips import Trip
from routes.models.stations import Station
from accounts.models.user_accounts import UserAccount  # Custom user model
from branches.models.branches import Branch


class Consignment(models.Model):
    """
    Consignment model managing the complete logistics lifecycle of long-distance parcel freight.
    
    Features:
    - Multi-tenancy Isolation: Securely partitioned via tenant_id.
    - Unique Traceability Triad: Enforces system-wide unique waybills, barcodes, and QR identifiers.
    - Multi-Station Routing: Links explicit point-of-origin and destination terminal hubs.
    - Dynamic Weight & Spatial Metrics: Tracks mass (KG) and volumetric displacement (M3) parameters.
    - Cod Financial Ledger: Monitors cash-on-delivery collection and accounting transfer pipelines.
    - Personnel Allocation Auditing: Tracks employee agents executing reception and ultimate dispatch delivery.
    
    Statuses:
    - RECEIVED: Parcel accepted at originating counter desk, stored in warehouse storage.
    - LOADED: Cargo assigned and physically packed into a specific vehicle's trunk space compartment.
    - IN_TRANSIT: The trip journey has departed, vehicle is actively driving on route.
    - ARRIVED: Vehicle arrived at destination station hub terminal, parcel unloaded to warehouse floor.
    - DELIVERED: Handed over successfully to receiver client, financial balances resolved.
    - RETURNED: Delivery failed, item returned back to original sender node location.
    - LOST: Risk alert; package failed to emerge during audit, marked missing in transit.
    - DAMAGED: Item physically broken or contents compromised during handling operations.
    
    Example:
        # Create a new parcel consignment draft with cash on delivery requirement
        parcel = Consignment.objects.create(
            tenant_id=1,
            waybill_code='WAY-20260530-X92A',
            sender_name='Nguyen Van A',
            sender_phone='0912345678',
            receiver_name='Tran Thi B',
            receiver_phone='0987654321',
            origin_station_id=5,
            destination_station_id=12,
            weight_kg=12.50,
            freight_charge=150000.00,
            cod_amount=500000.00,
            status='RECEIVED'
        )
    """

    STATUS_CHOICES = (
        ('RECEIVED', _('Received - Parcel accepted at origin counter hub branch warehouse')),
        ('LOADED', _('Loaded - Cargo packed and secured inside vehicle trunk compartment')),
        ('IN_TRANSIT', _('In Transit - Vehicle is actively navigating the trip route')),
        ('ARRIVED', _('Arrived - Unloaded at target destination station terminal floor')),
        ('DELIVERED', _('Delivered - Parcel successfully signed off and handed over to receiver')),
        ('RETURNED', _('Returned - Rejected or undeliverable, routed back to original sender')),
        ('LOST', _('Lost - Proximity search failed, marked missing in operations')),
        ('DAMAGED', _('Damaged - Structural package integrity broken or compromised during transit')),
    )

    # Using BigAutoField matches BIGSERIAL primary key target requirements
    id = models.BigAutoField(primary_key=True)
    
    # ========================================================================
    # RELATIONSHIPS & MULTI-TENANCY
    # ========================================================================
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,  # Matches ON DELETE CASCADE from requirement
        default=1,
        related_name='consignments',
        db_index=True,
        help_text='Tenant corporate owner holding legal data sovereignty over this cargo parcel log',
        db_comment='Multi-tenancy tenant reference'
    )
    
    trip = models.ForeignKey(
        Trip,
        on_delete=models.SET_NULL,  # Matches REFERENCES trips(id) ON DELETE SET NULL
        related_name='consignments',
        null=True,
        blank=True,
        db_index=True,  # Matches explicitly built index: idx_consignments_trip
        help_text='The active vehicle journey transit route assigned to convey this physical bưu kiện',
        db_comment='Soft reference mapping target dispatch vehicle trip'
    )
    
    origin_station = models.ForeignKey(
        Station,
        on_delete=models.SET_NULL,  # Matches REFERENCES stations(id) ON DELETE SET NULL
        related_name='origin_consignments',
        null=True,
        blank=True,
        help_text='The physical origin station hub node where the package was dropped off',
        db_comment='Soft reference mapping source station node'
    )
    
    destination_station = models.ForeignKey(
        Station,
        on_delete=models.SET_NULL,  # Matches REFERENCES stations(id) ON DELETE SET NULL
        related_name='destination_consignments',
        null=True,
        blank=True,
        help_text='The target destination station hub node where the parcel is destined to be picked up',
        db_comment='Soft reference mapping target station node'
    )
    
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,  # Matches REFERENCES branches(id) ON DELETE SET NULL
        related_name='consignments',
        null=True,
        blank=True,
        help_text='The physical corporate retail office terminal location currently managing the item lifecycle',
        db_comment='Soft reference mapping executing branch terminal office hub'
    )
    
    # ========================================================================
    # SECURITY INDICES & TRACEABILITY SCAN CODES
    # ========================================================================
    
    waybill_code = models.CharField(
        max_length=30,
        unique=True,  # Matches VARCHAR(30) NOT NULL UNIQUE
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9\-_]+$',
                message='Waybill tracking code must contain only uppercase letters, numbers, hyphens, and underscores'
            )
        ],
        help_text='Unique human-readable tracking index string token (e.g., WAY-1002-X89)',
        db_comment='Unique system logistics waybill identity token key code'
    )
    
    barcode = models.CharField(
        max_length=100,
        unique=True,  # Matches VARCHAR(100) UNIQUE
        null=True,
        blank=True,
        help_text='Standardized 1D barcode sequence mapped onto physical paper shipping labels for scanner guns',
        db_comment='Unique 1D barcode identification string sequence'
    )
    
    qr_code = models.CharField(
        max_length=100,
        unique=True,  # Matches VARCHAR(100) UNIQUE
        null=True,
        blank=True,
        help_text='High-density 2D matrix QR token enabling fast mobile camera manifest scans on bến bãi floors',
        db_comment='Unique 2D matrix QR token string sequence'
    )
    
    # ========================================================================
    # CUSTOMER CRM PROFILES (SENDER / RECEIVER)
    # ========================================================================
    
    sender_name = models.CharField(
        max_length=255,
        help_text='Full individual name or corporate company text shipping this package line',
        db_comment='Sender profile full identification name text'
    )
    
    sender_phone = models.CharField(
        max_length=20,
        db_index=True,  # Matches explicitly built index: idx_consignments_sender
        validators=[
            RegexValidator(
                regex=r'^\+?[0-9\s\-]{7,20}$',
                message='Sender phone contact compilation sequence is invalid'
            )
        ],
        help_text='Primary contact mobile number sequence tracking originating client accounts',
        db_comment='Sender telephone communication sequence string'
    )
    
    receiver_name = models.CharField(
        max_length=255,
        help_text='Full legal individual identity name authorized to claim or pull the package at target counters',
        db_comment='Target recipient full identification name text'
    )
    
    receiver_phone = models.CharField(
        max_length=20,
        db_index=True,  # Matches explicitly built index: idx_consignments_recv
        validators=[
            RegexValidator(
                regex=r'^\+?[0-9\s\-]{7,20}$',
                message='Receiver phone contact compilation sequence is invalid'
            )
        ],
        help_text='Primary mobile sequence utilized to dispatch arrival notice automated SMS text lines',
        db_comment='Target recipient telephone communication sequence string'
    )
    
    # ========================================================================
    # FREIGHT SPECS & METRICS
    # ========================================================================
    
    cargo_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text='Classification category grouping layout matching the pricing engine rules matrix (e.g., FRAGILE, NORMAL)',
        db_comment='Material composition categorization taxonomies string token'
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        help_text='Detailed content declarations required for freight safety checking (e.g., Red Asus Laptop inside leather sleeve)',
        db_comment='Declared content descriptive text logs'
    )
    
    weight_kg = models.DecimalField(
        max_digits=8,
        decimal_places=2,  # Matches NUMERIC(8,2)
        null=True,
        blank=True,
        validators=[MinValueValidator(0.01)],
        help_text='The physical scale mass value metric calculated in kilograms (KG)',
        db_comment='Actual measured physical scale mass weight parameter value'
    )
    
    volume_m3 = models.DecimalField(
        max_digits=8,
        decimal_places=3,  # Matches NUMERIC(8,3)
        null=True,
        blank=True,
        validators=[MinValueValidator(0.001)],
        help_text='Volumetric spatial calculation tracking dimensional capacity occupied inside chassis decks in cubic meters (M3)',
        db_comment='Computed volumetric displacement capacity spatial property value'
    )
    
    # ========================================================================
    # ACCUMULATED BALANCES & FINANCIAL LEDGER ARITHMETICS
    # ========================================================================
    
    declared_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,  # Matches NUMERIC(15,2)
        null=True,
        blank=True,
        validators=[MinValueValidator(0.00)],
        help_text='The customer estimated cash valuation of parcel properties used to establish safety liability caps',
        db_comment='Declared monetary asset liability evaluation cap'
    )
    
    freight_charge = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,  # Matches NUMERIC(15,2) NOT NULL DEFAULT 0
        validators=[MinValueValidator(0.00)],
        help_text='The core tariff transport operational fee invoice price assessed to move the cargo unit',
        db_comment='Base logistics transit service tariff rate currency value'
    )
    
    insurance_fee = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,  # Matches NUMERIC(15,2) NOT NULL DEFAULT 0
        validators=[MinValueValidator(0.00)],
        help_text='Surcharge applied to high-value items protecting the tenant against financial indemnity claims',
        db_comment='Administrative asset security indemnity processing fee currency value'
    )
    
    # ========================================================================
    # CASH ON DELIVERY (COD) CONTROL ENGINE
    # ========================================================================
    
    cod_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,  # Matches NUMERIC(15,2) NOT NULL DEFAULT 0
        validators=[MinValueValidator(0.00)],
        help_text='Cash-on-delivery collection threshold target to collect from receiver before handover approval',
        db_comment='Target Cash-on-delivery currency balance requested by sender'
    )
    
    cod_collected = models.BooleanField(
        default=False,  # Matches NOT NULL DEFAULT FALSE
        help_text='Boolean verification flag logging if counter clerk physically captured the cash during delivery handover',
        db_comment='Cash-on-delivery physical capture execution status boolean switch flag'
    )
    
    cod_transferred = models.BooleanField(
        default=False,  # Matches NOT NULL DEFAULT FALSE
        help_text='Accounting audit flag confirming system successfully transferred collected COD funds back into sender accounts',
        db_comment='Cash-on-delivery bank settlement back to originating client verification switch'
    )
    
    # ========================================================================
    # WORKFLOW PROGRESSION LIFECYCLES
    # ========================================================================
    
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='RECEIVED',
        db_index=True,  # Matches explicitly built index: idx_consignments_status
        help_text='The current logistics lifecycle milestone phase tracking this parcel through processing grids',
        db_comment='Workflow tracking operational progress status taxonomy string token'
    )
    
    notes = models.TextField(
        null=True,
        blank=True,
        help_text='Operational alerts such as secondary recipient authorization notes or localized damage annotations',
        db_comment='Administrative logistics textual log annotations'
    )
    
    # ========================================================================
    # PERSONNEL ALLOCATION ARITHMETICS & CHRONOLOGY AUDITS
    # ========================================================================
    
    received_by = models.ForeignKey(
        UserAccount,
        on_delete=models.SET_NULL,  # Matches REFERENCES user_accounts(id) ON DELETE SET NULL
        related_name='received_consignments',
        null=True,
        blank=True,
        help_text='The intake desk clerk user profile account who scanned the parcel into origin storage inventory',
        db_comment='Reference to origin intake employee account profile'
    )
    
    delivered_by = models.ForeignKey(
        UserAccount,
        on_delete=models.SET_NULL,  # Matches REFERENCES user_accounts(id) ON DELETE SET NULL
        related_name='delivered_consignments',
        null=True,
        blank=True,
        help_text='The delivery window desk counter agent who confirmed cash capture and handed parcel to customer',
        db_comment='Reference to destination handover employee account profile'
    )
    
    received_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timezone-aware timestamp logging exactly when intake clerks committed initial entry protocols',
        db_comment='Intake warehouse entrance timestamp execution log'
    )
    
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timezone-aware timestamp logging exactly when final client signed off the delivery certificate',
        db_comment='Ultimate delivery dispatch timestamp confirmation log'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='System record logging anchor tracking exactly when this record line row entered the main database',
        db_comment='Creation timestamp'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,  # Emulates SELECT create_updated_at_trigger('consignments'); application-side automation
        help_text='Timestamp tracking exactly when attributes inside this logistics row node were modified',
        db_comment='Last database row tracking mutation modification timestamp'
    )

    class Meta:
        db_table = 'consignments'
        verbose_name = _('Cargo Consignment')
        verbose_name_plural = _('Cargo Consignments')
        ordering = ['-created_at', 'waybill_code']
        
        # ====================================================================
        # CONSTRAINTS & META INDEX OVERRIDES
        # ====================================================================
        
        constraints = [
            # Direct database CHECK constraint matching CONSTRAINT chk_consignment_status
            models.CheckConstraint(
                check=models.Q(status__in=['RECEIVED', 'LOADED', 'IN_TRANSIT', 'ARRIVED', 'DELIVERED', 'RETURNED', 'LOST', 'DAMAGED']),
                name='chk_consignment_status'
            ),
            # Financial safety constraints: Numerical balances cannot reflect absolute negative parameters
            models.CheckConstraint(
                check=models.Q(freight_charge__gte=0) & models.Q(insurance_fee__gte=0) & models.Q(cod_amount__gte=0),
                name='chk_consignment_money_positive'
            )
        ]

    def __str__(self):
        """String representation"""
        return f"[{self.waybill_code}] {self.sender_name} -> {self.receiver_name} ({self.status})"

    # ========================================================================
    # PRODUCTION LOGISTICS STATE MACHINE ENGINE WORKFLOWS
    # ========================================================================

    def clean(self):
        """
        Application-layer integrity checks validating data layout parameters before serialization locks.
        """
        super().clean()
        
        if self.origin_station_id and self.destination_station_id and self.origin_station_id == self.destination_station_id:
            raise ValidationError({
                'destination_station': _('Logistics Layout Error: Target destination station cannot be physically identical to origin station nodes.')
            })
            
        if self.cod_transferred and not self.cod_collected:
            raise ValidationError({
                'cod_transferred': _('Accounting Discrepancy: COD funds cannot reflect successful transfer statuses prior to physical cash collection processing.')
            })

    def execute_cargo_loading(self, target_trip_instance):
        """
        Transitions package into vehicle fleet trunk spaces. 
        Locks trip linkages and escalates tracking state to LOADED.
        """
        if self.status != 'RECEIVED':
            raise ValidationError(_("Logistics Exception: Cargo cannot be packed onto vehicles unless it sits under a RECEIVED warehouse state."))
            
        self.trip = target_trip_instance
        self.status = 'LOADED'
        self.save(update_fields=['trip', 'status', 'updated_at'])

    def execute_delivery_handover(self, dispatch_agent_user, collected_cod_cash=0.00):
        """
        Executes terminal counter handover protocols. Verifies cash-on-delivery requirements,
        stamps chronology data markers, allocates personnel, and closes out tracking states.
        """
        if self.status not in ['ARRIVED', 'RECEIVED']: # Support both standard long-haul and localized direct hub pickups
            raise ValidationError(_("Logistics Exception: Cannot dispatch delivery logs for parcels that have not arrived at local station terminal floors."))
            
        from django.utils import timezone
        from decimal import Decimal
        
        # Financial validation gate check: If COD is required, ensure cash collection parameters match targets
        if self.cod_amount > 0 and not self.cod_collected:
            input_cash = Decimal(str(collected_cod_cash))
            if input_cash < self.cod_amount:
                raise ValidationError(_("Financial Error: Cannot release parcel. Handover input cash balance fails to clear the specified COD milestone requirements."))
            self.cod_collected = True

        self.status = 'DELIVERED'
        self.delivered_by = dispatch_agent_user
        self.delivered_at = timezone.now()
        
        self.save(update_fields=['status', 'cod_collected', 'delivered_by', 'delivered_at', 'updated_at'])
        
        # Telematics system trigger point: Automatically dispatch transactional push notifications 
        # or SMS alerts informing the sender that their bưu kiện has been claimed successfully.