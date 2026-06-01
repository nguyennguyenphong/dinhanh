# ============================================================================
# FILE: apps/employees/models.py
# Shift Types Management Models
# ============================================================================

from datetime import datetime

from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

class ShiftType(models.Model):
    """
    ShiftType model defining operational working hours configurations per tenant.

    Features:
    - Multi-tenancy: Securely partitioned via tenant_id
    - Code Identification: Unique identifier string code per tenant scope
    - Timeline Boundaries: Manages strict daily start and end working time limits
    - Overnight Intelligence: Flag to signal if a shift spans across midnight boundary
    - High-Performance Indexing: Built for fast timeline checking and schedule filtering

    Example:
        # Create a standard day shift (08:00 AM -> 05:00 PM)
        day_shift = ShiftType.objects.create(
            tenant_id=1,
            code='DAY_SHIFT',
            name='Standard Day Shift',
            start_time='08:00:00',
            end_time='17:00:00',
            is_overnight=False
        )

        # Create an overnight night shift (10:00 PM -> 06:00 AM next day)
        night_shift = ShiftType.objects.create(
            tenant_id=1,
            code='NIGHT_SHIFT',
            name='Overnight Night Shift',
            start_time='22:00:00',
            end_time='06:00:00',
            is_overnight=True
        )
    """

    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS & MULTI-TENANCY
    # ========================================================================

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,  # Matches ON DELETE CASCADE from requirement
        default=1,
        related_name="shift_types",
        db_index=True,
        help_text="Tenant owner of this operational shift type configuration",
    )

    # ========================================================================
    # SHIFT TAXONOMY & CODES
    # ========================================================================

    code = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r"^[A-Z0-9\-_]+$",
                message="Code must contain only uppercase letters, numbers, hyphens, and underscores",
            )
        ],
        help_text="Unique operational shift code identifier per tenant (e.g., MORNING, NIGHT_01)",
    )

    name = models.CharField(
        max_length=100,
        help_text="Human readable display name of the shift schedule pattern",
    )

    # ========================================================================
    # TIMELINE MATRIX (DAILY WORKING BOUNDARIES)
    # ========================================================================

    start_time = models.TimeField(
        help_text="The official clock time when the work shift begins"
    )

    end_time = models.TimeField(
        help_text="The official clock time when the work shift ends"
    )

    is_overnight = models.BooleanField(
        default=False,
        help_text="Designates whether the shift boundary spans across midnight (e.g., 22:00 to 06:00 next day)",
    )

    # ========================================================================
    # TIMESTAMPS
    # ========================================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Timestamp when this shift configuration template was created",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when this shift configuration parameters were last modified",
    )

    class Meta:
        db_table = "shift_types"
        verbose_name = _("Shift Type")
        verbose_name_plural = _("Shift Types")
        ordering = ["tenant", "start_time", "code"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Unique shift configuration code per tenant (Matches UNIQUE (tenant_id, code))
            models.UniqueConstraint(
                fields=["tenant", "code"], name="unique_tenant_shift_type_code"
            ),
        ]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Composite index optimized for roster filters looking up shifts by specific timeline blocks
            models.Index(
                fields=["tenant", "start_time", "end_time"],
                name="idx_shift_timeline_lookup",
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"[{self.code}] {self.name} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"

    # ========================================================================
    # BUSINESS LOGIC & TIME CALCULATION METHODS
    # ========================================================================

    def save(self, *args, **kwargs):
        """
        Overriding save method to automatically deduce and enforce the 'is_overnight'
        property if it wasn't manually calculated at application boundary layers.
        """
        if self.start_time and self.end_time:
            # If start time is later than or equal to end time, it is inherently an overnight shift
            if self.start_time >= self.end_time:
                self.is_overnight = True
            else:
                self.is_overnight = False

        super().save(*args, **kwargs)

    def calculate_duration_minutes(self):
        """
        Calculate total net working time duration mapped in minutes.
        Handles standard and complex overnight cross-midnight calculations seamlessly.

        Returns:
            Integer (Total shift duration in minutes)
        """
        if not self.start_time or not self.end_time:
            return 0

        # Convert daily time objects into abstract calculation datetime structures
        today = datetime.today()
        start_dt = datetime.combine(today, self.start_time)

        if self.is_overnight:
            # End time belongs to the subsequent calendar date
            from datetime import timedelta

            end_dt = datetime.combine(today, self.end_time) + timedelta(days=1)
        else:
            end_dt = datetime.combine(today, self.end_time)

        duration = end_dt - start_dt
        return int(duration.total_seconds() / 60)

    # ========================================================================
    # CLASSMETHODS / SCHEDULING LOGIC QUERIES
    # ========================================================================

    @classmethod
    def get_overnight_shifts(cls, tenant_id):
        """
        Fetch all cross-midnight configured shifts under a specific corporate enterprise tenant.

        Args:
            tenant_id: Integer

        Returns:
            QuerySet of ShiftType objects
        """
        return cls.objects.filter(tenant_id=tenant_id, is_overnight=True)
