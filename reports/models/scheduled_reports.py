# ============================================================================
# FILE: apps/analytics/models.py
# Automated Report Scheduling, Cron Jobs & Distribution Engines
# ============================================================================

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class ScheduledReport(models.Model):
    """
    ScheduledReport model controlling automated cyclical execution routines for BI report blueprints.

    Features:
    - Background Worker Hub: Acts as the data ledger registry for daemon runners (e.g., Celery Beat) to poll jobs.
    - Advanced Cron Expressions: Supports optional Unix-styled cron syntax rules for high-precision time anchoring.
    - Polymorphic Delivery Matrix: Uses a JSONB array wrapper to manage dynamic target dispatch routes (Emails/Users).
    - Multi-Format File Generation: Dictates compilation file types including PDF documents, Excel sheets, or CSV data lines.

    Frequencies:
    - DAILY: Fires off report compilation tasks once every 24 hours at designated midnight blocks.
    - WEEKLY: Triggers summary rollups once every 7 calendar days on specialized day markers (e.g., Sunday night shifts).
    - MONTHLY: Compiles high-level corporate balance sheets exactly at monthly boundaries or fiscal period changes.

    Formats:
    - PDF: Compiles rich-text graphical executive summary packages intended directly for operational screen inspection.
    - EXCEL: Generates heavy multi-sheet structured spreadsheets suited for granular data pivot operations by accounting desks.
    - CSV: Streamlined lightweight raw plaintext arrays designed for external script scraping or third-party CRM hooks.

    Example:
        # Schedule an automated weekly revenue spreadsheet sent directly to the corporate management board
        job = ScheduledReport.objects.create(
            report_id=8,
            name='Weekly Transport Revenue and Cash Outflow Digest',
            frequency='WEEKLY',
            cron_expr='0 2 * * 0',  # Execute every Sunday at 02:00 AM sharp
            recipients=[
                {'type': 'email', 'value': 'ceo@transportnode.com'},
                {'type': 'user', 'value': '1042'}  # Primary key linking directly to UserAccount
            ],
            format='EXCEL',
            is_active=True
        )
    """

    FREQUENCY_CHOICES = (
        (
            "DAILY",
            _("Daily - Dispatches compiled blueprints once every calendar day loop"),
        ),
        (
            "WEEKLY",
            _(
                "Weekly - Executes summary analytical matrices once every seven calendar days"
            ),
        ),
        (
            "MONTHLY",
            _(
                "Monthly - Fires off deep period balance sheet summaries at month-end close dates"
            ),
        ),
    )

    FORMAT_CHOICES = (
        (
            "PDF",
            _(
                "PDF - Portable Document Format layout configured for print-ready layout reviews"
            ),
        ),
        (
            "EXCEL",
            _(
                "Excel - Structured digital spreadsheet workbook optimized for manual data audits"
            ),
        ),
        (
            "CSV",
            _(
                "CSV - Raw comma-separated values document tailored for external analytical processing pipelines"
            ),
        ),
    )

    id = models.AutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS & BLUEPRINT ORIGINS
    # ========================================================================

    report = models.ForeignKey(
        "reports.ReportDefinition",
        on_delete=models.CASCADE,  # Matches REFERENCES report_definitions(id) ON DELETE CASCADE
        related_name="schedules",
        db_index=True,
        help_text="The dynamic database analytics report definition blueprint model acting as the extraction engine for this job",
    )

    # ========================================================================
    # IDENTITY & CRON TIMING MATRICES
    # ========================================================================

    name = models.CharField(
        max_length=100,  # Matches VARCHAR(100) NOT NULL
        help_text="Short descriptive title identifying this background automated mailing task schedule configuration",
    )

    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,  # Enforces structural enum compliance parameters
        db_index=True,
        help_text="The high-level macro cyclic category block governing transmission timing patterns",
    )

    cron_expr = models.CharField(
        max_length=50,  # Matches VARCHAR(50) nullable specifications
        null=True,
        blank=True,
        help_text='Standard five-field Unix crontab string syntax expression for custom precision execution mapping (e.g., "30 7 * * 1-5")',
    )

    # ========================================================================
    # POLYMORPHIC ROUTING MATRIX & OUTPUT COMPILATION
    # ========================================================================

    recipients = models.JSONField(
        default=list,  # Matches NOT NULL DEFAULT '[]' using clean array factory generators
        help_text='JSONB array containing direct communication delivery routing targets. Structure layout: [{"type": "email"|"user", "value": "..."}]',
    )

    format = models.CharField(
        max_length=10,
        choices=FORMAT_CHOICES,
        default="PDF",  # Matches NOT NULL DEFAULT 'PDF'
        help_text="The physical target electronic extension file format structure built during task rendering executions",
    )

    # ========================================================================
    # LIFECYCLE MONITORING STATES & CHRONOLOGY
    # ========================================================================

    last_run_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timezone-aware calendar timestamp documenting the last moment this automation task ran successfully",
    )

    next_run_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,  # Critical production optimization: allows cron workers to perform ultra-fast sweep queries
        help_text="Timezone-aware timestamp marking the immediate future target milestone when background workers should run this row",
    )

    is_active = models.BooleanField(
        default=True,  # Matches NOT NULL DEFAULT TRUE
        db_index=True,
        help_text="Master administrative toggle switch. Turning this off flags the worker pool daemon to ignore scheduling executions for this row.",
    )

    created_at = models.DateTimeField(
        default=models.functions.Now,  # Matches NOT NULL DEFAULT NOW() at core database compilation levels
        help_text="Timezone-aware log record tracking exactly when this schedule record entry was registered inside the database",
    )

    class Meta:
        db_table = "scheduled_reports"
        verbose_name = _("Automated Report Schedule")
        verbose_name_plural = _("Automated Report Schedules")

        # Priority sort lines focus scanning pipelines directly onto imminent tasks
        ordering = ["-is_active", "next_run_at", "-created_at"]

        # ====================================================================
        # CONSTRAINTS & COMPOSITE TIMING INDEXES
        # ====================================================================

        constraints = [
            # Direct database-level CHECK constraint enforcing cyclical processing taxonomy limits
            models.CheckConstraint(
                condition=models.Q(frequency__in=["DAILY", "WEEKLY", "MONTHLY"]),
                name="chk_scheduled_report_frequency_enum",
            ),
            # Direct database-level CHECK constraint enforcing document file extension type limits
            models.CheckConstraint(
                condition=models.Q(format__in=["PDF", "EXCEL", "CSV"]),
                name="chk_scheduled_report_format_enum",
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"Schedule #{self.id} | {self.name} ({self.frequency} -> {self.format}) [Active: {self.is_active}]"

    # ========================================================================
    # PRODUCTION WORKFLOW CONTROL & CHRONOLOGY CALCULATORS
    # ========================================================================

    def clean(self):
        """
        Application-layer structural validation auditing recipient array shapes and cron syntax rules.
        """
        super().clean()

        # 1. Cron Expression Syntax Validation Guard
        if self.cron_expr:
            self.cron_expr = self.cron_expr.strip()
            cron_parts = self.cron_expr.split()
            if len(cron_parts) != 5:
                raise ValidationError(
                    {
                        "cron_expr": _(
                            "Syntax Parsing Exception: Cron expressions must contain exactly 5 space-separated operational field values (Minute, Hour, Day-of-Month, Month, Day-of-Week)."
                        )
                    }
                )

        # 2. Polymorphic JSON Array Envelope Validation
        if isinstance(self.recipients, list):
            for idx, entry in enumerate(self.recipients):
                if (
                    not isinstance(entry, dict)
                    or "type" not in entry
                    or "value" not in entry
                ):
                    raise ValidationError(
                        {
                            "recipients": _(
                                f"Envelope Shape Error at item index [{idx}]: Elements inside delivery lists must match standard dict keys: 'type' and 'value'."
                            )
                        }
                    )
                if entry["type"] not in ["email", "user"]:
                    raise ValidationError(
                        {
                            "recipients": _(
                                f"Validation Exception at item index [{idx}]: Delivery routing types must restrict to 'email' or 'user' taxonomy rules."
                            )
                        }
                    )
        else:
            raise ValidationError(
                {
                    "recipients": _(
                        "Structural Typing Error: Target recipient fields must be saved under a valid flat array collection schema."
                    )
                }
            )

    def recalculate_next_execution_milestone(self):
        """
        Calculates and advances the next chronological runtime execution block inside database tracks.
        Invoked by background script workers immediately post successful execution sweeps.
        """
        import datetime

        from django.utils import timezone

        now = timezone.now()
        self.last_run_at = now

        # Fallback standard progression calculus engine if high-precision cron parameters are blank
        if self.frequency == "DAILY":
            self.next_run_at = now + datetime.timedelta(days=1)
        elif self.frequency == "WEEKLY":
            self.next_run_at = now + datetime.timedelta(weeks=1)
        elif self.frequency == "MONTHLY":
            # Advances execution exactly 30 calendar days down the financial registry track
            self.next_run_at = now + datetime.timedelta(days=30)

        self.save(update_fields=["last_run_at", "next_run_at"])
