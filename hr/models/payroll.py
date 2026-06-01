# ============================================================================
# FILE: apps/payroll/models.py
# Payroll Ledger Management Models
# ============================================================================

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Payroll(models.Model):
    """
    Payroll model acting as the official financial ledger for monthly employee compensation.

    Features:
    - Temporal Segmentation: Tracks explicit calendar year and month parameters
    - High-Precision Ledger: Leverages Decimal fields for all base, variable, and deduction nodes
    - Auto-Calculation Matrix: Enforces core accounting formulas at application boundary layers
    - Unique Constraint: Limits an employee to exactly one payroll ledger sheet per specific month

    Statuses:
    - DRAFT: Initial generation statement, subject to adjustments and recalculations
    - APPROVED: Verified by HR/Finance, locked against changes, awaiting payout execution
    - PAID: Disbursement successfully completed, tracking settlement timestamps

    Formula:
        Net Salary = Base Salary + Allowances + Overtime Pay + Bonus
                     - Deductions - Insurance Deduct - Tax Deduct

    Example:
        # Create a draft payroll slip
        slip = Payroll.objects.create(
            employee=employee_instance,
            period_year=2026,
            period_month=5,
            working_days=22.0,
            base_salary=15000000.00,
            allowances=2000000.00,
            overtime_pay=1500000.00,
            insurance_deduct=1575000.00,
            tax_deduct=500000.00,
            bonus=1000000.00
        )
    """

    STATUS_CHOICES = (
        ("DRAFT", _("Draft - Statement under review or recalculation")),
        ("APPROVED", _("Approved - Verified by management, locked for payout")),
        ("PAID", _("Paid - Fund disbursement successfully executed")),
    )

    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS & AUDITS
    # ========================================================================

    employee = models.ForeignKey(
        "hr.Employee",
        on_delete=models.CASCADE,  # Matches ON DELETE CASCADE from requirement
        related_name="payrolls",
        db_index=True,
        help_text="The employee asset whose monthly earnings are calculated",
    )

    approved_by = models.ForeignKey(
        "accounts.UserAccount",
        on_delete=models.SET_NULL,  # Matches ON DELETE SET NULL from requirement
        related_name="approved_payrolls",
        null=True,
        blank=True,
        db_index=True,
        help_text="The financial or HR authority account signing off on this statement line",
    )

    # ========================================================================
    # TEMPORAL MATRIX PERIODS
    # ========================================================================

    period_year = models.PositiveSmallIntegerField(
        help_text="The specific calendar tracking year for this payment cycle (e.g., 2026)"
    )

    period_month = models.PositiveSmallIntegerField(
        help_text="The specific calendar tracking month for this payment cycle (1 to 12)"
    )

    # ========================================================================
    # ATTENDANCE METRICS METADATA
    # ========================================================================

    working_days = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=0.0,  # Matches NUMERIC(4,1) supporting fractional inputs like 21.5 working days
        help_text="Total cumulative productive attendance days logged in the current cycle month",
    )

    # ========================================================================
    # EARNINGS BLOCKS (ADDITIONS)
    # ========================================================================

    base_salary = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,  # Matches NUMERIC(15,2)
        help_text="Contractual fixed base salary allocated for the standard cycle period",
    )

    allowances = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text="Total standard recurring allowances (e.g., lunch, fuel, phone support)",
    )

    overtime_pay = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text="Total accrued compensation generated from approved overtime working hour shifts",
    )

    bonus = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text="Discretionary performance bonuses, commissions, or milestone incentives",
    )

    # ========================================================================
    # REDUCTIONS BLOCKS (DEDUCTIONS)
    # ========================================================================

    deductions = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text="Standard internal deductions (e.g., disciplinary fines, asset damages, advanced payroll draws)",
    )

    insurance_deduct = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text="Employee-borne statutory social, health, and unemployment insurance co-pay withholding",
    )

    tax_deduct = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text="Calculated Personal Income Tax (PIT) withholding value scheduled for state treasury remittance",
    )

    # ========================================================================
    # THE NET REVENUE MATRICES (THE BOTTOM LINE)
    # ========================================================================

    net_salary = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text="The definitive final take-home net earnings payable to the employee after arithmetic reduction rules",
    )

    # ========================================================================
    # FLOW STATUSES, TIMESTAMPS & LOGS
    # ========================================================================

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="DRAFT",
        db_index=True,
        help_text="The workflow stage representing review pipeline status tracking",
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timezone-aware timestamp logging exactly when financial bank wire transaction occurred",
    )

    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Internal auditing annotations explaining specific modifications, tax exceptions, or formulas",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this payroll statement row was originally generated",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the compensation profile entries were last modified",
    )

    class Meta:
        db_table = "payroll"
        verbose_name = _("Payroll")
        verbose_name_plural = _("Payrolls")
        ordering = ["-period_year", "-period_month", "employee"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Enforces exactly one ledger record per employee per cycle month (Matches UNIQUE (employee_id, period_year, period_month))
            models.UniqueConstraint(
                fields=["employee", "period_year", "period_month"],
                name="unique_employee_payroll_period",
            ),
        ]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Composite index specialized for high-speed calculation dashboard overview filters
            models.Index(
                fields=["period_year", "period_month", "status"],
                name="idx_pay_period_status_lookup",
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.employee.full_name} - {self.period_month}/{self.period_year} ({self.status})"

    # ========================================================================
    # LEDGER ENGINE ACCOUNTING METHODS
    # ========================================================================

    def calculate_net_salary(self):
        """
        Execute core mathematical deduction matrix rules to isolate net salary balance.

        Returns:
            Decimal (Calculated net revenue)
        """
        additions = self.base_salary + self.allowances + self.overtime_pay + self.bonus
        subtractions = self.deductions + self.insurance_deduct + self.tax_deduct
        return max(additions - subtractions, 0.00)

    def save(self, *args, **kwargs):
        """
        Overriding standard save pipeline to auto-calculate net salary
        and protect financial records from manual floating calculations gaps.
        """
        # Always enforce application formula before persisting ledger cells
        self.net_salary = self.calculate_net_salary()
        super().save(*args, **kwargs)

    def clean(self):
        """
        Enforce business sanity barriers before serialization layers.
        """
        super().clean()
        if self.period_month < 1 or self.period_month > 12:
            raise ValidationError(
                {
                    "period_month": _(
                        "The period month must fall strictly between indices 1 and 12."
                    )
                }
            )

        if self.status == "PAID" and not self.paid_at:
            raise ValidationError(
                {
                    "paid_at": _(
                        "A statement flagged as PAID must feature an explicit transaction execution timestamp."
                    )
                }
            )

    def lock_and_approve(self, supervisor_user):
        """
        Transition workflow state to APPROVED. Ready for wire execution pipelines.

        Args:
            supervisor_user: UserAccount model instance
        """
        if self.status != "DRAFT":
            raise ValidationError(
                _(
                    "Only statements in DRAFT can be locked and transitioned to APPROVED."
                )
            )

        self.status = "APPROVED"
        self.approved_by = supervisor_user
        self.save(update_fields=["status", "approved_by", "updated_at"])

    def mark_as_disbursed(self):
        """
        Finalize ledger lifecycle. Wire payout confirmed, close account book line.
        """
        if self.status != "APPROVED":
            raise ValidationError(
                _(
                    "Payroll statements must be explicitly APPROVED by management before registering payouts."
                )
            )

        from django.utils import timezone

        self.status = "PAID"
        self.paid_at = timezone.now()
        self.save(update_fields=["status", "paid_at", "updated_at"])

    # ========================================================================
    # CLASSMETHODS / LEDGER SUMMARY METRICS PIPELINES
    # ========================================================================

    @classmethod
    def get_total_monthly_payout_volume(cls, tenant_id, year, month):
        """
        Sum aggregate financial net exposure allocated under a specific cycle month per tenant.

        Args:
            tenant_id: Integer
            year: Integer
            month: Integer

        Returns:
            Decimal (Total budget required)
        """
        return (
            cls.objects.filter(
                employee__tenant_id=tenant_id,
                period_year=year,
                period_month=month,
                status__in=["APPROVED", "PAID"],
            ).aggregate(total_net=models.Sum("net_salary"))["total_net"]
            or 0.00
        )
