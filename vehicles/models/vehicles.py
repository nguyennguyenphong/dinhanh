# ============================================================================
# FILE: apps/vehicles/models.py
# Vehicles Management Models
# ============================================================================

from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from safedelete.models import SOFT_DELETE_CASCADE, SafeDeleteModel


class Vehicle(SafeDeleteModel):
    """
    Vehicle model for managing individual assets within a fleet per tenant.

    Features:
    - Multi-tenancy: Securely partitioned via tenant_id
    - Unique Identifiers: Unique plate_number enforced at DB level
    - Category & Location: Relates to a VehicleCategory and operating Branch
    - Compliance Tracking: Expiry tracking for registration, insurance, and inspection
    - Status Lifecycle: Regulated via database-level CHECK constraints

    Statuses:
    - AVAILABLE: Ready for trip assignment
    - IN_TRIP: Currently executing a trip
    - MAINTENANCE: Undergoing service, repairs, or inspections
    - INACTIVE: Temporarily pulled out of operation
    - DISPOSED: Permanently removed from fleet (sold, scrapped)

    Example:
        # Create a new vehicle
        vehicle = Vehicle.objects.create(
            tenant_id=1,
            plate_number='29A-12345',
            category=vip_category,
            status='AVAILABLE',
            odometer_km=15200.50
        )

        # Check if compliance documents are expiring
        is_expired = vehicle.has_expired_documents()
    """

    _safedelete_policy = SOFT_DELETE_CASCADE

    STATUS_CHOICES = (
        ("AVAILABLE", _("Available - Ready for service")),
        ("IN_TRIP", _("In Trip - Currently operational on a route")),
        ("MAINTENANCE", _("Maintenance - In garage or workshop")),
        ("INACTIVE", _("Inactive - Temporarily decommissioned")),
        ("DISPOSED", _("Disposed - Permanently out of fleet")),
    )

    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS & MULTI-TENANCY
    # ========================================================================

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        default=1,
        related_name="vehicles",
        db_index=True,
        help_text="Tenant owner of this vehicle",
    )

    category = models.ForeignKey(
        "vehicles.VehicleCategory",
        on_delete=models.RESTRICT,
        related_name="vehicles",
        db_index=True,
        help_text="Vehicle specification category profile",
    )

    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        related_name="vehicles",
        null=True,
        blank=True,
        db_index=True,
        help_text="Current managing or home branch location",
    )

    # ========================================================================
    # CORE VEHICLE IDENTIFICATION
    # ========================================================================

    plate_number = models.CharField(
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[A-Z0-9\-.\s]+$", message="Plate number format is invalid"
            )
        ],
        help_text="Unique official vehicle license plate number (e.g., 29A-123.45)",
    )

    vin = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Vehicle Identification Number (Chassis number)",
    )

    # ========================================================================
    # ASSET SPECIFICATIONS
    # ========================================================================

    manufacture_year = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="Year of manufacture/production"
    )

    brand = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Manufacturer brand (e.g., Hyundai, Thaco, Ford)",
    )

    model = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Specific manufacturing model name",
    )

    color = models.CharField(
        max_length=50, null=True, blank=True, help_text="Exterior color description"
    )

    # ========================================================================
    # OPERATIONS, COMPLIANCE & STATUS
    # ========================================================================

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="AVAILABLE",
        db_index=True,
        help_text="Current technical or operation lifecycle state",
    )

    odometer_km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total cumulative tracked mileage in kilometers",
    )

    registration_expiry = models.DateField(
        null=True,
        blank=True,
        help_text="Expiry date of the vehicle official legal registration",
    )

    insurance_expiry = models.DateField(
        null=True,
        blank=True,
        help_text="Expiry date of the vehicle civil liability/hull insurance policy",
    )

    inspection_expiry = models.DateField(
        null=True,
        blank=True,
        help_text="Expiry date of the vehicle technical safety inspection certificate",
    )

    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Internal operational logs, repair flags, or general annotations",
    )

    # ========================================================================
    # TIMESTAMPS
    # ========================================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Timestamp when the vehicle asset profile was registered",
    )

    updated_at = models.DateTimeField(
        auto_now=True, help_text="Timestamp when the vehicle profile data was modified"
    )

    class Meta:
        db_table = "vehicles"
        verbose_name = _("Vehicle")
        verbose_name_plural = _("Vehicles")
        ordering = ["tenant", "-created_at"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Direct database-level CHECK constraint for status alignment
            models.CheckConstraint(
                condition=models.Q(
                    status__in=[
                        "AVAILABLE",
                        "IN_TRIP",
                        "MAINTENANCE",
                        "INACTIVE",
                        "DISPOSED",
                    ]
                ),
                name="chk_vehicle_status",
            )
        ]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Optimization for matching operational ready trucks/buses by branch
            models.Index(fields=["branch", "status"], name="idx_vehicle_branch_status"),
            # Optimization for compliance pipelines (cronjobs checking upcoming alerts)
            models.Index(
                fields=["inspection_expiry", "insurance_expiry"],
                name="idx_vehicle_compliance_dates",
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.plate_number} - {self.brand or ''} {self.model or ''}".strip()

    # ========================================================================
    # FLEET MANAGEMENT LOGIC METHODS
    # ========================================================================

    def update_odometer(self, current_km):
        """
        Safely update cumulative fleet asset odometer.

        Args:
            current_km: Decimal or Float
        """
        if current_km and (self.odometer_km is None or current_km >= self.odometer_km):
            self.odometer_km = current_km
            self.save(update_fields=["odometer_km", "updated_at"])

    def has_expired_documents(self):
        """
        Verify if any core compliance documents have passed expiry threshold.

        Returns:
            Boolean
        """
        from django.utils import timezone

        today = timezone.localdate()

        return any(
            [
                self.registration_expiry and self.registration_expiry < today,
                self.insurance_expiry and self.insurance_expiry < today,
                self.inspection_expiry and self.inspection_expiry < today,
            ]
        )

    # ========================================================================
    # CLASSMETHODS / QUERY METHODS
    # ========================================================================

    @classmethod
    def get_by_status(cls, tenant_id, status_string):
        """
        Fetch vehicle assets targeted under an operational segment.

        Args:
            tenant_id: Integer
            status_string: String ('AVAILABLE', 'MAINTENANCE', etc.)

        Returns:
            QuerySet of Vehicle objects
        """
        return cls.objects.filter(
            tenant_id=tenant_id, status=status_string
        ).select_related("category", "branch")

    @classmethod
    def get_expiring_compliance_fleet(cls, tenant_id, days_threshold=15):
        """
        Fetch active vehicles whose inspection certificate is expiring within a timeframe.

        Args:
            tenant_id: Integer
            days_threshold: Integer (days window)

        Returns:
            QuerySet of Vehicle objects
        """
        from datetime import timedelta

        from django.utils import timezone

        target_date = timezone.localdate() + timedelta(days=days_threshold)
        return cls.objects.filter(
            tenant_id=tenant_id,
            status__in=["AVAILABLE", "IN_TRIP"],
            inspection_expiry__lte=target_date,
        )
