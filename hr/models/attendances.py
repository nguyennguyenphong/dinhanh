# ============================================================================
# FILE: apps/employees/models.py
# Attendance Tracking Management Models
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

# Assuming these models exist in your production architecture
from hr.models.employees import Employee
from hr.models.shift_types import ShiftType
from accounts.models.user_accounts import UserAccount  # Custom user model


class Attendance(models.Model):
    """
    Attendance model for tracking employee daily clock-in/out times, locations, and statuses.

    Features:
    - Shift Context: Associated with a ShiftType to measure puncture discrepancies
    - Temporal Matrix: Stores work date and timezone-aware timestamps (TIMESTAMPTZ)
    - Geo-fencing Ready: Records high-precision GPS coordinates (lat/lng) during check-in
    - Audit Trail: Tracks authorization/approval signatures via approved_by
    - Unique Constraint: Limits an employee to exactly one attendance record per work calendar day

    Statuses:
    - PRESENT: Logged hours successfully met requirements
    - ABSENT: Employee failed to appear without approved leave
    - LATE: Clock-in occurred after the designated shift start time threshold
    - HALF_DAY: Worked only half of the scheduled operational hours
    - LEAVE: On approved paid or unpaid leave (e.g., medical, annual)
    - HOLIDAY: Public statutory corporate holiday compliance assignment

    Example:
        # Create an attendance record
        record = Attendance.objects.create(
            employee=employee_instance,
            shift_type=shift_type_instance,
            work_date='2026-05-30',
            check_in='2026-05-30T07:55:00+07:00',
            check_in_lat=10.762622,
            check_in_lng=106.660172,
            status='PRESENT'
        )
    """

    STATUS_CHOICES = (
        ("PRESENT", _("Present - Full day completed")),
        ("ABSENT", _("Absent - Missing shift")),
        ("LATE", _("Late - Clocked in past shift start time")),
        ("HALF_DAY", _("Half Day - Partial shift attendance")),
        ("LEAVE", _("Leave - Approved dynamic day off")),
        ("HOLIDAY", _("Holiday - Scheduled public or corporate holiday")),
    )

    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,  # Matches ON DELETE CASCADE from requirement
        related_name="attendances",
        db_index=True,
        help_text="The employee asset profile this log sheet maps to",
    )

    shift_type = models.ForeignKey(
        ShiftType,
        on_delete=models.SET_NULL,  # Matches ON DELETE SET NULL
        related_name="attendances",
        null=True,
        blank=True,
        db_index=True,
        help_text="The planned working timeframe configuration target schema",
    )

    approved_by = models.ForeignKey(
        UserAccount,
        on_delete=models.SET_NULL,  # Matches ON DELETE SET NULL
        related_name="approved_attendances",
        null=True,
        blank=True,
        db_index=True,
        help_text="The administrative authority account signing off or adjusting this record",
    )

    # ========================================================================
    # TEMPORAL MATRIX (DATE & TIME ENTRIES)
    # ========================================================================

    work_date = models.DateField(
        db_index=True,
        help_text="The targeted calendar date context for this schedule log entry",
    )

    check_in = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timezone-aware timestamp capturing the exact check-in puncture",
    )

    check_out = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timezone-aware timestamp capturing the exact check-out puncture",
    )

    # ========================================================================
    # GEOGRAPHIC LOCATION METADATA (GPS COORDINATES)
    # ========================================================================

    check_in_lat = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="High-precision GPS latitude coordinate parsed at check-in node",
    )

    check_in_lng = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        help_text="High-precision GPS longitude coordinate parsed at check-in node",
    )

    # ========================================================================
    # STATUS & CORRECTIONS
    # ========================================================================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PRESENT",
        db_index=True,
        help_text="Operational status classifying compliance of the logging day metrics",
    )

    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Annotations detailing late reasons, geo-location errors, or adjustments",
    )

    # ========================================================================
    # SYSTEM AUDITS
    # ========================================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this attendance ledger line was opened in system",
    )

    class Meta:
        db_table = "attendances"
        verbose_name = _("Attendance")
        verbose_name_plural = _("Attendances")
        ordering = ["-work_date", "employee"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Limits exactly one attendance row per employee per date (Matches UNIQUE (employee_id, work_date))
            models.UniqueConstraint(
                fields=["employee", "work_date"], name="unique_employee_work_date"
            ),
        ]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Highly critical index optimizing core time-tracking sheets and monthly payroll pipelines
            models.Index(
                fields=["work_date", "status"], name="idx_att_date_status_metrics"
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.employee.full_name} - {self.work_date} ({self.get_status_display()})"

    # ========================================================================
    # TIME CALCULATION & COMPLIANCE METHODS
    # ========================================================================

    def get_total_hours_worked(self):
        """
        Calculate net hours logged between active puncture milestones.

        Returns:
            Float (Duration hours value) or None
        """
        if self.check_in and self.check_out:
            duration = self.check_out - self.check_in
            return round(duration.total_seconds() / 3600.0, 2)
        return None

    def execute_admin_override(self, supervisor_user, target_status, audit_notes):
        """
        Safely register manual overrides driven by administrative audit workflows.

        Args:
            supervisor_user: UserAccount model instance
            target_status: String choice from STATUS_CHOICES
            audit_notes: String explaining adjustment framework
        """
        self.status = target_status
        self.approved_by = supervisor_user
        self.notes = (
            f"[Adjusted by Admin]: {audit_notes}"
            if self.notes is None
            else f"{self.notes} | [Adjusted]: {audit_notes}"
        )
        self.save(update_fields=["status", "approved_by", "notes"])

    # ========================================================================
    # CLASSMETHODS / ROSTER DATA PIPELINES
    # ========================================================================

    @classmethod
    def get_monthly_roster_by_employee(cls, employee_id, year, month):
        """
        Fetch chronological timesheet logs targeting an active calculation month.

        Args:
            employee_id: Integer
            year: Integer
            month: Integer

        Returns:
            QuerySet of Attendance objects
        """
        return (
            cls.objects.filter(
                employee_id=employee_id, work_date__year=year, work_date__month=month
            )
            .select_related("shift_type", "approved_by")
            .order_by("work_date")
        )
