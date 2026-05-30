# ============================================================================
# FILE: apps/vehicles/models.py
# Vehicle Categories Management Models
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.contrib.postgres.fields import ArrayField  # Production feature for PostgreSQL TEXT[]

# Assuming this model exists in your production architecture
from tenants.models.tenants import Tenant


class VehicleCategory(models.Model):
    """
    VehicleCategory model for grouping vehicles with shared specifications.
    
    Features:
    - Multi-tenancy: Partitioned securely via tenant_id
    - Unique Constraint: Unique code identifier per tenant
    - Type Classification: Strictly checked types (BUS, SLEEPER_BUS, LIMOUSINE, etc.)
    - Amenities Tracking: Native PostgreSQL array support for amenities strings
    - High-Performance Indexing: Built for fast operational filtering
    
    Vehicle Types:
    - BUS: Standard seating bus
    - SLEEPER_BUS: Bus equipped with beds/berths
    - LIMOUSINE: Luxury high-end transport vehicle
    - MINIBUS: Small capacity passenger van/bus
    - OTHER: Miscellaneous or custom vehicle type
    
    Example:
        # Create a category
        category = VehicleCategory.objects.create(
            tenant_id=1,
            code='VIP-SLEEP-34',
            name='Luxury 34-Sleeper Cabin',
            seat_count=34,
            vehicle_type='SLEEPER_BUS',
            amenities=['wifi', 'ac', 'usb', 'toilet', 'blanket']
        )
        
        # Check if an amenity is available
        has_wifi = category.has_amenity('wifi')
    """

    VEHICLE_TYPE_CHOICES = (
        ('BUS', _('Bus - Standard Seating Bus')),
        ('SLEEPER_BUS', _('Sleeper Bus - Cabin/Bed Bus')),
        ('LIMOUSINE', _('Limousine - Luxury Vehicle')),
        ('MINIBUS', _('Minibus - Small Capacity Van')),
        ('OTHER', _('Other - Custom Vehicle Type')),
    )

    id = models.BigAutoField(primary_key=True)
    
    # ========================================================================
    # RELATIONSHIPS & MULTI-TENANCY
    # ========================================================================
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        default=1,
        related_name='vehicle_categories',
        db_index=True,
        help_text='Tenant owner of this vehicle category'
    )
    
    # ========================================================================
    # CATEGORY IDENTIFICATION
    # ========================================================================
    
    code = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9\-_]+$',
                message='Code must contain only uppercase letters, numbers, hyphens, and underscores'
            )
        ],
        help_text='Unique category code per tenant (e.g., STD-45, VIP-22)'
    )
    
    name = models.CharField(
        max_length=100,
        help_text='Display name of the category'
    )
    
    # ========================================================================
    # SPECIFICATIONS & FEATURES
    # ========================================================================
    
    seat_count = models.PositiveSmallIntegerField(
        help_text='Total number of passenger seats/berths available'
    )
    
    vehicle_type = models.CharField(
        max_length=50,
        choices=VEHICLE_TYPE_CHOICES,
        db_index=True,
        help_text='Classification type of the vehicle'
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        help_text='Detailed description of the category and its configuration'
    )
    
    # Native PostgreSQL array field to support TEXT[]
    amenities = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list,
        help_text='List of available features (e.g., wifi, ac, usb, tv)'
    )
    
    # ========================================================================
    # STATUS & TIMESTAMPS
    # ========================================================================
    
    is_active = models.BooleanField(
        default=True,
        help_text='Designates whether this category is active and can be assigned to new vehicles'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='Timestamp when the category was created'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp when the category was last modified'
    )

    class Meta:
        db_table = 'vehicle_categories'
        verbose_name = _('Vehicle Category')
        verbose_name_plural = _('Vehicle Categories')
        ordering = ['tenant', 'vehicle_type', 'code']
        
        # ====================================================================
        # CONSTRAINTS
        # ====================================================================
        
        constraints = [
            # Unique code per tenant (Matches UNIQUE (tenant_id, code))
            models.UniqueConstraint(
                fields=['tenant', 'code'],
                name='unique_tenant_vehicle_category_code'
            ),
            # Direct database-level CHECK constraint for vehicle_type safety
            models.CheckConstraint(
                condition=models.Q(
                    vehicle_type__in=[
                        'BUS',
                        'SLEEPER_BUS',
                        'LIMOUSINE',
                        'MINIBUS',
                        'OTHER'
                    ]
                ),
                name='chk_vehicle_type'
            )
        ]
        
        # ====================================================================
        # INDEXES
        # ====================================================================
        
        indexes = [
            # Composite index for filtering operational/active categories per tenant quickly
            models.Index(
                fields=['tenant', 'is_active'],
                name='idx_veh_cat_tenant_active'
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"[{self.code}] {self.name} ({self.seat_count} seats)"

    # ========================================================================
    # AMENITIES HELPER METHODS
    # ========================================================================

    def has_amenity(self, amenity_name):
        """
        Check if a specific amenity string exists in the category list.
        
        Args:
            amenity_name: String (case-insensitive check)
            
        Returns:
            Boolean
        """
        if not self.amenities:
            return False
        return amenity_name.lower() in [a.lower() for a in self.amenities]

    def add_amenity(self, amenity_name):
        """
        Safely append a new unique amenity to the category array.
        
        Args:
            amenity_name: String
        """
        amenity_clean = amenity_name.strip()
        if amenity_clean and amenity_clean not in self.amenities:
            self.amenities.append(amenity_clean)
            self.save(update_fields=['amenities', 'updated_at'])

    # ========================================================================
    # CLASSMETHODS / QUERY METHODS
    # ========================================================================

    @classmethod
    def get_active_by_tenant(cls, tenant_id):
        """
        Fetch all active vehicle categories for a specific tenant.
        
        Args:
            tenant_id: Integer
            
        Returns:
            QuerySet of VehicleCategory objects
        """
        return cls.objects.filter(tenant_id=tenant_id, is_active=True)

    @classmethod
    def filter_by_amenity(cls, tenant_id, amenity_name):
        """
        Advanced Query: Leverage PostgreSQL array filtering capabilities 
        via Django's native '__contains' lookup to find categories with an amenity.
        
        Args:
            tenant_id: Integer
            amenity_name: String
            
        Returns:
            QuerySet of VehicleCategory objects
            
        Example:
            wifi_buses = VehicleCategory.filter_by_amenity(1, 'wifi')
        """
        return cls.objects.filter(tenant_id=tenant_id, amenities__contains=[amenity_name])