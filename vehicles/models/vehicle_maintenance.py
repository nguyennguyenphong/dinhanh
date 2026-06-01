# ============================================================================
# FILE: apps/vehicles/models.py
# Vehicle Maintenance Management Models
# ============================================================================

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class VehicleMaintenance(models.Model):
    """
    VehicleMaintenance model for logging mechanical service, repairs, and inspections.

    Features:
    - Asset Tracking: Strongly bound to an individual Vehicle instance
    - Technical Auditing: Records garage/vendor details, mileage logs, and costs
    - Operations History: Tracks who (UserAccount) authorized/performed the service
    - Next Due Intelligence: Stores thresholds for future scheduled maintenance (date/km)
    - Data Integrity: Strict database-level CHECK constraints for types and statuses

    Maintenance Types:
    - SCHEDULED: Routine preventive care (e.g., oil changes, periodic tune-ups)
    - EMERGENCY: Unplanned reactive repairs due to breakdown or damage
    - INSPECTION: Technical safety or operational compliance checks
    - CLEANING: Routine commercial valeting or deep detailing service

    Statuses:
    - PENDING: Job card created, waiting for garage slot or authorization
    - IN_PROGRESS: Mechanics currently performing the service
    - DONE: Service finished, paperwork complete, assets ready for field
    - CANCELLED: Maintenance canceled or reassigned

    Example:
        # Create a new maintenance record
        log = VehicleMaintenance.objects.create(
            vehicle=vehicle_instance,
            type='SCHEDULED',
            description='10,000 km Periodic Engine Service and Filter Replacement',
            cost=2500000.00,
            odometer_in=10050.20,
            scheduled_at='2026-06-01',
            status='PENDING'
        )
    """

    TYPE_CHOICES = (
        ("SCHEDULED", _("Scheduled - Preventive maintenance")),
        ("EMERGENCY", _("Emergency - Unplanned breakthrough repairs")),
        ("INSPECTION", _("Inspection - Diagnostic safety check")),
        ("CLEANING", _("Cleaning - Commercial valeting service")),
    )

    STATUS_CHOICES = (
        ("PENDING", _("Pending - Awaiting slot or approval")),
        ("IN_PROGRESS", _("In Progress - Vehicle in workshop")),
        ("DONE", _("Done - Maintenance successfully completed")),
        ("CANCELLED", _("Cancelled - Operation aborted")),
    )

    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    vehicle = models.ForeignKey(
        "vehicles.Vehicle",
        on_delete=models.CASCADE,
        related_name="maintenances",
        db_index=True,
        help_text="The specific vehicle asset undergoing maintenance",
    )

    performed_by = models.ForeignKey(
        "accounts.UserAccount",
        on_delete=models.SET_NULL,
        related_name="supervised_maintenances",
        null=True,
        blank=True,
        db_index=True,
        help_text="The staff member or technician responsible for managing this operation",
    )

    # ========================================================================
    # SERVICE DETAILS & TAXONOMY
    # ========================================================================

    type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        db_index=True,
        help_text="Classification categories distinguishing service context",
    )

    description = models.TextField(
        help_text="Detailed logs explaining mechanical faults, parts swapped, or work scope"
    )

    cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total cumulative monetary value billed for parts and labor",
    )

    vendor = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Name of the external garage, workshop, or third-party service provider",
    )

    # ========================================================================
    # ODOMETER TRACKING (MILEAGE MATRIX)
    # ========================================================================

    odometer_in = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Odometer reading when the vehicle entered the workshop",
    )

    odometer_out = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Odometer reading when the vehicle left the workshop",
    )

    # ========================================================================
    # LIFECYCLE TIMESTAMPS & SCHEDULES
    # ========================================================================

    scheduled_at = models.DateField(
        null=True,
        blank=True,
        help_text="Target date on which this maintenance task is planned to occur",
    )

    completed_at = models.DateField(
        null=True,
        blank=True,
        help_text="Official date when the job card was signed off as completed",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
        db_index=True,
        help_text="Operational stage representing current job progression state",
    )

    # ========================================================================
    # PREDICTIVE NEXT DUE THRESHOLDS
    # ========================================================================

    next_due_km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Predicted mileage target threshold when the asset must return for the next cycle",
    )

    next_due_date = models.DateField(
        null=True,
        blank=True,
        help_text="Calendar target date dead-line when the asset must return for the next cycle",
    )

    # ========================================================================
    # SYSTEM AUDITS
    # ========================================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Timestamp when this job log sheet was originally opened in system",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the workflow profile entries were last modified",
    )

    class Meta:
        db_table = "vehicle_maintenance"
        verbose_name = _("Vehicle Maintenance")
        verbose_name_plural = _("Vehicle Maintenances")
        ordering = ["-scheduled_at", "-created_at"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Direct database-level CHECK constraints for absolute data integrity
            models.CheckConstraint(
                condition=models.Q(
                    type__in=["SCHEDULED", "EMERGENCY", "INSPECTION", "CLEANING"]
                ),
                name="chk_maintenance_type",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    status__in=["PENDING", "IN_PROGRESS", "DONE", "CANCELLED"]
                ),
                name="chk_maintenance_status",
            ),
        ]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Optimizes performance for asset dashboard looking up chronological repair history
            models.Index(fields=["vehicle", "status"], name="idx_maint_vehicle_status"),
            # Optimizes reporting engines filtering by calendar windows
            models.Index(
                fields=["scheduled_at", "completed_at"],
                name="idx_maint_timeline_metrics",
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"[{self.type}] {self.vehicle.plate_number} - {self.status} ({self.scheduled_at or 'Unscheduled'})"

    # ========================================================================
    # WORKFLOW AND FLEET ENGINE SYNCHRONIZATION METHODS
    # ========================================================================

    def clean(self):
        """
        Validate business rules at application layer before saving to DB.
        """
        super().clean()
        if self.odometer_in and self.odometer_out:
            if self.odometer_out < self.odometer_in:
                raise ValidationError(
                    {
                        "odometer_out": _(
                            "Check-out odometer cannot be lower than check-in mileage."
                        )
                    }
                )

    def complete_maintenance(self, final_odometer, final_cost=None):
        """
        Safely transition maintenance state to DONE and synchronize the parent vehicle's data.

        Args:
            final_odometer: Decimal or Float (Odometer reading at check-out)
            final_cost: Decimal or Float (Optional final repair invoice)

        Example:
            log.complete_maintenance(final_odometer=12500.80, final_cost=3200000.00)
        """
        from django.utils import timezone

        self.odometer_out = final_odometer
        if final_cost is not None:
            self.cost = final_cost

        self.status = "DONE"
        self.completed_at = timezone.localdate()
        self.save(
            update_fields=[
                "odometer_out",
                "cost",
                "status",
                "completed_at",
                "updated_at",
            ]
        )

        # Push update to master asset data engine
        self.vehicle.update_odometer(final_odometer)
        if self.vehicle.status == "MAINTENANCE":
            self.vehicle.status = "AVAILABLE"
            self.vehicle.save(update_fields=["status", "updated_at"])

    # ========================================================================
    # CLASSMETHODS / DATA AGGREGATION LOGIC
    # ========================================================================

    @classmethod
    def get_total_expenses(cls, tenant_id, start_date=None, end_date=None):
        """
        Calculate total sum expenditures across a period for a tenant.

        Args:
            tenant_id: Integer
            start_date: Date object
            end_date: Date object

        Returns:
            Decimal (Total spent currency value)
        """
        query = Q(vehicle__tenant_id=tenant_id, status="DONE", cost__isnull=False)
        if start_date:
            query &= Q(completed_at__gte=start_date)
        if end_date:
            query &= Q(completed_at__lte=end_date)

        return (
            cls.objects.filter(query).aggregate(total=models.Sum("cost"))["total"]
            or 0.00
        )
