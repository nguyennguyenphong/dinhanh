# ============================================================================
# FILE: apps/vehicles/models.py
# Seat Maps Management Models
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

# Assuming this model exists in your production architecture
from vehicles.models.vehicle_categories import VehicleCategory


class SeatMap(models.Model):
    """
    SeatMap model for managing physical or logical grid layouts of vehicle categories.
    
    Features:
    - Structural Association: Deeply bound to a VehicleCategory definition
    - JSONB Support: Native Django JSONField mapped to PostgreSQL JSONB for layout matrices
    - Flexibility: Scalable configuration for rows, columns, floors, and special seat types
    - High-Performance Indexing: GIN indexing capability suggested for internal JSON property queries
    
    Layout Config Structure Example:
        {
            "floors": 1,
            "grid": {
                "rows": 10,
                "columns": 4
            },
            "seats": [
                {"id": "A1", "row": 1, "col": 1, "type": "STANDARD"},
                {"id": "A2", "row": 1, "col": 4, "type": "STANDARD"},
                {"id": "VIP1", "row": 2, "col": 2, "type": "PREMIUM"}
            ]
        }
    
    Example:
        # Create a seat map layout
        seat_map = SeatMap.objects.create(
            category=vip_bus_category,
            name='Standard 34-Cabin Upper-Floor Blueprint',
            total_seats=34,
            layout_config={
                "floors": 2,
                "matrix_version": "v1.0"
            }
        )
        
        # Validate if configuration is synchronized with the assigned total seats
        is_valid = seat_map.validate_seat_count()
    """

    id = models.BigAutoField(primary_key=True)
    
    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================
    
    category = models.ForeignKey(
        VehicleCategory,
        on_delete=models.CASCADE,  # Matches ON DELETE CASCADE from requirement
        related_name='seat_maps',
        db_index=True,
        help_text='Vehicle category profile this schematic blueprint applies to',
    )
    
    # ========================================================================
    # SCHEMA METADATA
    # ========================================================================
    
    name = models.CharField(
        max_length=100,
        help_text='Descriptive title of the layout configuration template (e.g., Standard 2+2 Layout)',
    )
    
    total_seats = models.PositiveSmallIntegerField(
        help_text='Declared number of total sellable seats configured inside this map blueprint',
    )
    
    # Native PostgreSQL JSONB architecture integration
    layout_config = models.JSONField(
        default=dict,  # Standard factory for empty object initialization '{}'
        help_text='Complex data object matrix capturing row, col, type, floor and specific coordinate structures',
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='Timestamp when the schematic layout structure template was registered',
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp when the schema configuration matrix was last modified',
    )

    class Meta:
        db_table = 'seat_maps'
        verbose_name = _('Seat Map')
        verbose_name_plural = _('Seat Maps')
        ordering = ['category', 'name']
        
        # ====================================================================
        # INDEXES
        # ====================================================================
        
        indexes = [
            # Compound index for locating targeted blueprint mapping templates quickly
            models.Index(
                fields=['category', 'name'],
                name='idx_seat_map_lookup',
            ),
            # Note for Advanced Production: If query capabilities on internal components of 'layout_config'
            # are heavily required, a django.contrib.postgres.indexes.GinIndex can be substituted here.
        ]

    def __str__(self):
        """String representation"""
        return f"{self.name} - ({self.total_seats} seats)"

    # ========================================================================
    # BUSINESS LOGIC & STRUCTURAL INTEGRITY VALIDATION METHODS
    # ========================================================================

    def validate_seat_count(self):
        """
        Validate if the explicit integer count matches the embedded elements inside the JSON matrix.
        
        Returns:
            Boolean
        """
        if not self.layout_config or 'seats' not in self.layout_config:
            return False
            
        seats_list = self.layout_config.get('seats', [])
        return len(seats_list) == self.total_seats

    def get_seat_identifiers(self):
        """
        Extract flat list arrays of unique string identities for engine synchronization.
        
        Returns:
            List of Strings (e.g., ['A1', 'A2', 'B1', 'B2'])
        """
        if not self.layout_config or 'seats' not in self.layout_config:
            return []
            
        return [seat.get('id') for seat in self.layout_config.get('seats', []) if 'id' in seat]

    # ========================================================================
    # CLASSMETHODS / TEMPLATE QUERY LOGIC
    # ========================================================================

    @classmethod
    def get_maps_by_category(cls, category_id):
        """
        Fetch registered template specifications assigned underneath a localized vehicle segment.
        
        Args:
            category_id: Integer
            
        Returns:
            QuerySet of SeatMap objects
        """
        return cls.objects.filter(category_id=category_id).order_by('-created_at')