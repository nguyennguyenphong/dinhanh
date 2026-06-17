# ============================================================================
# FILE: apps/employees/models.py
# Leave Requests Management Models
# ============================================================================

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel


class LeaveRequest(BaseModel):
    """
    LeaveRequest model for managing employee time-off, sick leaves, and legal absences.

    Features:
    - Tracking Duration: Manages absolute start/end date bounds alongside exact days fractional counts
    - Administrative Sign-off: Captures supervisor decision workflows (approved_by, approved_at)
    - Data Integrity: Strict database-level CHECK constraints for leave categories and statuses
    - Business Rules Validation: Application-layer validation for date ranges and sequence flows

    Leave Types:
    - ANNUAL: Standard paid vacation leave allocation
    - SICK: Certified medical or health-related absence
    - UNPAID: Non-compensated personal time-off
    - MATERNITY: Statutory parental/maternity leave lifecycle
    - COMPASSIONATE: Bereavement or urgent family crisis allowance

    Statuses:
    - PENDING: Request submitted, awaiting supervisor verification
    - APPROVED: Authorized by management, days will deduct from employee balance
    - REJECTED: Turned down by management with historical logs
    - CANCELLED: Aborted or withdrawn by the employee before execution

    Example:
        # Create a new leave application request
        request = LeaveRequest.objects.create(
            employee=employee_instance,
            leave_type='ANNUAL',
            from_date='2026-06-15',
            to_date='2026-06-16',
            days_count=2.0,
            reason='Family summer vacation plan'
        )
    """


    LEAVE_TYPE_CHOICES = (
        ("ANNUAL", _("Annual - Paid Vacation Time")),
        ("SICK", _("Sick - Medical/Health Absence")),
        ("UNPAID", _("Unpaid - Non-compensated Leave")),
        ("MATERNITY", _("Maternity - Statutory Parental Leave")),
        ("COMPASSIONATE", _("Compassionate - Special/Bereavement Leave")),
    )

    STATUS_CHOICES = (
        ("PENDING", _("Pending - Awaiting Review")),
        ("APPROVED", _("Approved - Authorized and Confirmed")),
        ("REJECTED", _("Rejected - Declined by Reviewer")),
        ("CANCELLED", _("Cancelled - Withdrawn by Employee")),
    )

    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    employee = models.ForeignKey(
        "hr.Employee",
        on_delete=models.CASCADE,  # Matches ON DELETE CASCADE from requirement
        related_name="leave_requests",
        db_index=True,
        help_text="The employee asset lodging this time-off request application",
    )

    approved_by = models.ForeignKey(
        "accounts.UserAccount",
        on_delete=models.SET_NULL,  # Matches ON DELETE SET NULL from requirement
        related_name="reviewed_leaves",
        null=True,
        blank=True,
        db_index=True,
        help_text="The administrative management account signing off on this decision profile",
    )

    # ========================================================================
    # TIME-OFF TAXONOMY & METRICS
    # ========================================================================

    leave_type = models.CharField(
        max_length=30,
        choices=LEAVE_TYPE_CHOICES,
        db_index=True,
        help_text="Classification category determining compensation and matrix handling",
    )

    from_date = models.DateField(
        help_text="The inclusive starting calendar date bound for the leave duration window"
    )

    to_date = models.DateField(
        help_text="The inclusive ending calendar date bound for the leave duration window"
    )

    days_count = models.DecimalField(
        max_digits=4,
        decimal_places=1,  # Matches NUMERIC(4,1) supporting fractional inputs like 1.5, 0.5 days
        help_text="Calculated fractional decimal metric totaling net absences (e.g., 0.5 for half day)",
    )

    reason = models.TextField(
        null=True,
        blank=True,
        help_text="Contextual statement provided by applicant explaining absence requirements",
    )

    # ========================================================================
    # LIFECYCLE PROGRESSION & AUDIT METADATA
    # ========================================================================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
        db_index=True,
        help_text="Workflow progression state measuring administrative review status",
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timezone-aware timestamp logging exactly when authorization occurred",
    )

    class Meta:
        db_table = "leave_requests"
        verbose_name = _("Leave Request")
        verbose_name_plural = _("Leave Requests")
        ordering = ["-created_at", "employee"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Direct database-level CHECK constraints for absolute structural data integrity
            models.CheckConstraint(
                condition=models.Q(
                    leave_type__in=[
                        "ANNUAL",
                        "SICK",
                        "UNPAID",
                        "MATERNITY",
                        "COMPASSIONATE",
                    ]
                ),
                name="chk_leave_type",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    status__in=["PENDING", "APPROVED", "REJECTED", "CANCELLED"]
                ),
                name="chk_leave_status",
            ),
        ]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Composite index optimized for HR approval managers reviewing pending logs chronologically
            models.Index(
                fields=["status", "-created_at"], name="idx_leave_review_pipeline"
            ),
            # Index for quick scanning of seasonal overlapping intervals within operational schedules
            models.Index(
                fields=["from_date", "to_date"], name="idx_leave_calendar_window"
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.employee.full_name} - {self.get_leave_type_display()} ({self.days_count} Days): {self.status}"

    # ========================================================================
    # BUSINESS LOGIC & CONTEXT VALIDATION METHODS
    # ========================================================================

    def clean(self):
        """
        Application-layer constraint compliance parsing boundary rules before commits.
        """
        super().clean()
        if self.from_date and self.to_date:
            if self.from_date > self.to_date:
                raise ValidationError(
                    {
                        "to_date": _(
                            "The end date boundary cannot precede the start date matrix."
                        )
                    }
                )

            # Business logic validation: ensure days_count is positive value context
            if self.days_count and self.days_count <= 0:
                raise ValidationError(
                    {
                        "days_count": _(
                            "The requested day count must represent a positive scalar value."
                        )
                    }
                )

    def process_review_decision(self, supervisor_user, decision_status):
        """
        Safely execute workflow transitions driving state modifications on the leave ledger.

        Args:
            supervisor_user: UserAccount model instance
            decision_status: String matching choices ('APPROVED', 'REJECTED')

        Example:
            application.process_review_decision(manager, 'APPROVED')
        """
        if self.status != "PENDING":
            raise ValidationError(
                _(
                    "This application record has already left the PENDING processing state."
                )
            )

        from django.utils import timezone

        self.status = decision_status
        self.approved_by = supervisor_user
        self.approved_at = timezone.now()
        self.save(update_fields=["status", "approved_by", "approved_at", "updated_at"])

        # Integration hook point: Inject logic here to auto-deduct allocation ledger metrics
        # or propagate notifications via signals out to external dispatching nodes.

    # ========================================================================
    # CLASSMETHODS / DATA PIPELINES ANALYSIS
    # ========================================================================

    @classmethod
    def get_active_absences_by_date(cls, target_date):
        """
        Fetch approved active staff absences overlapping a designated operational date.
        Extremely useful for scheduling algorithms validating driver availability pools.

        Args:
            target_date: Date object

        Returns:
            QuerySet of LeaveRequest objects with optimized prefetched employee nodes
        """
        return cls.objects.filter(
            status="APPROVED", from_date__lte=target_date, to_date__gte=target_date
        ).select_related("employee")
