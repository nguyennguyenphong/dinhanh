# ============================================================================
# FILE: apps/vehicles/models.py
# Individual Seats Management Models
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

# Assuming this model exists in your production architecture
from vehicles.models.seat_maps import SeatMap


class Seat(models.Model):
    """
    Seat model representing an individual physical seat unit mapped inside a SeatMap template.
    
    Features:
    - Template Association: Linked directly to a specific SeatMap configuration
    - Unique Constraints: Ensures a seat code is unique within a unique seat map scope
    - Grid & Deck Coordinates: Supports rows, columns, and multiple floors/decks (e.g., lower vs. upper deck)
    - Graphic Positioning: Captures precise X/Y numeric scalars used for custom UI rendering layouts (SVG/Canvas)
    - Data Integrity: Strict database-level CHECK constraints for status and types
    
    Seat Types:
    - SEAT: Standard traditional passenger chair
    - BED: Sleeper berth or horizontal mattress cabin
    - VIP: Luxury high-comfort accommodation unit
    - PREMIUM: Middle-tier upgraded seating space
    
    Example:
        # Create an individual seat unit
        seat = Seat.objects.create(
            seat_map=seat_map_instance,
            seat_code='A01',
            seat_type='BED',
            deck=1,
            row_num=1,
            col_num=1,
            position_x=12.50,
            position_y=45.00
        )
    """

    SEAT_TYPE_CHOICES = (
        ('SEAT', _('Seat - Standard sitting chair')),
        ('BED', _('Bed - Sleeper berth cabin')),
        ('VIP', _('VIP - Ultra luxury private space')),
        ('PREMIUM', _('Premium - Enhanced comfort seating')),
    )

    id = models.BigAutoField(primary_key=True)
    
    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================
    
    seat_map = models.ForeignKey(
        SeatMap,
        on_delete=models.CASCADE,  # Matches ON DELETE CASCADE from requirement
        related_name='seats',
        db_index=True,
        help_text='The blueprint seat map configuration template this unit belongs to',
        db_comment='Reference to parent seat map template'
    )
    
    # ========================================================================
    # SEAT IDENTIFICATION
    # ========================================================================
    
    seat_code = models.CharField(
        max_length=10,
        help_text='Unique identifier code displayed to customer (e.g., A1, 12B, VIP-01)',
        db_comment='Seat physical code identifier'
    )
    
    seat_type = models.CharField(
        max_length=30,
        choices=SEAT_TYPE_CHOICES,
        default='SEAT',
        db_index=True,
        help_text='Classification type representing comfort spec and pricing tier',
        db_comment='Classification seat type string'
    )
    
    # ========================================================================
    # GRID SPATIAL COORDINATES
    # ========================================================================
    
    deck = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text='Deck/Floor layer identifier (e.g., 1 for Lower Deck, 2 for Upper Deck)',
        db_comment='Deck or floor number index'
    )
    
    row_num = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text='Matrix grid logical row sequence coordinate index number',
        db_comment='Logical row index number'
    )
    
    col_num = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text='Matrix grid logical column sequence coordinate index number',
        db_comment='Logical column index number'
    )
    
    # ========================================================================
    # GRAPHIC UI POSITIONING (SVG/CANVAS RENDERING)
    # ========================================================================
    
    position_x = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Absolute or relative graphic coordinate factor mapping onto X horizontal axis',
        db_comment='UI grid positioning coordinate absolute X'
    )
    
    position_y = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Absolute or relative graphic coordinate factor mapping onto Y vertical axis',
        db_comment='UI grid positioning coordinate absolute Y'
    )
    
    # ========================================================================
    # OPERATIONAL INITIAL STATUS
    # ========================================================================
    
    is_available = models.BooleanField(
        default=True,
        help_text='Designates whether this seat template unit is structurally ready for commercial usage',
        db_comment='Operational physical inventory status availability flag'
    )

    class Meta:
        db_table = 'seats'
        verbose_name = _('Seat')
        verbose_name_plural = _('Seats')
        ordering = ['seat_map', 'deck', 'row_num', 'col_num', 'seat_code']
        
        # ====================================================================
        # CONSTRAINTS
        # ====================================================================
        
        constraints = [
            # Enforces uniqueness of a seat identifier code inside a single map layout (Matches UNIQUE (seat_map_id, seat_code))
            models.UniqueConstraint(
                fields=['seat_map', 'seat_code'],
                name='unique_seat_map_code'
            ),
            # Direct database-level CHECK constraint enforcing predefined strict type entries
            models.CheckConstraint(
                check=models.Q(seat_type__in=['SEAT', 'BED', 'VIP', 'PREMIUM']),
                name='chk_seat_type'
            )
        ]
        
        # ====================================================================
        # INDEXES
        # ====================================================================
        
        indexes = [
            # Composite index specialized for high-velocity lookups when loading operational grids per deck layout
            models.Index(
                fields=['seat_map', 'deck', 'is_available'],
                name='idx_seat_map_deck_operational',
                db_comment='Fetch active commercial configurations map structure'
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.seat_code} ({self.get_seat_type_display()}) [Deck {self.get_deck_layer_name()}]"

    # ========================================================================
    # BUSINESS LOGIC & INTERPOLATION LOGS
    # ========================================================================

    def get_deck_layer_name(self):
        """
        Human readable interpretation helper mapping structural layers.
        
        Returns:
            String
        """
        return "Lower" if self.deck == 1 else "Upper"

    def get_vector_coordinates(self):
        """
        Extract numeric point tuple for custom vector/SVG layout generation nodes.
        
        Returns:
            Tuple (X, Y) or None
        """
        if self.position_x is not None and self.position_y is not None:
            return float(self.position_x), float(self.position_y)
        return None

    # ========================================================================
    # CLASSMETHODS / INVENTORY FETCH LOGIC
    # ========================================================================

    @classmethod
    def get_available_seats_by_map(cls, seat_map_id):
        """
        Fetch available seat configurations mapped beneath a shared architectural setup.
        
        Args:
            seat_map_id: Integer
            
        Returns:
            QuerySet of Seat objects
        """
        return cls.objects.filter(seat_map_id=seat_map_id, is_available=True).order_by('deck', 'row_num', 'col_num')