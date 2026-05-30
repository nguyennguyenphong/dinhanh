# ============================================================================
# FILE: apps/finance/models.py
# Corporate Finance, Expense Tracking & Cash Outflow Models
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

# Assuming these models exist in your production architecture
from tenants.models.tenants import Tenant
from financials.models.expense_categories import ExpenseCategory
from vehicles.models.vehicles import Vehicle
from trips.models.trips import Trip
from branches.models.branches import Branch
from hr.models.employees import Employee
from accounts.models.user_accounts import UserAccount  # Custom user model


class Expense(models.Model):
    """
    Expense model logging and auditing all corporate operational cash outlays.
    
    Features:
    - Multi-Dimensional Accounting: Tracks cost targets simultaneously across fleet, trips, branches, or personnel.
    - Currency Precision Audit: Eliminates float rounding errors via structured Numeric fields.
    - Two-Phase Approval Locking: Secures submission-to-approval workflows with explicit audit trails.
    - Document Cloud Linkage: Stashes external digital file path assets for formal fiscal tax audits.
    
    Statuses:
    - PENDING: Document is newly recorded by staff, awaiting executive manager review and approval.
    - APPROVED: Budget allocation cleared by finance desk, stashed in queue awaiting physical cash/bank release.
    - REJECTED: Disallowed by auditing staff. Disbursal aborted permanently; requires parameter adjustments.
    - PAID: Financial transaction completed; cash removed from cash register or bank clearing webhooks matched.
    
    Example:
        # Log a fuel transaction receipt bound directly to a specific vehicle and trip pipeline
        cost_line = Expense.objects.create(
            tenant_id=1,
            category_id=4,  # e.g., FUEL_DIESEL category
            vehicle_id=12,  # e.g., Bus plate 29B-12345
            trip_id=9810,   # e.g., Trip Hanoi - Danang
            title='Diesel refuel at station #3',
            amount=2450000.00,
            expense_date='2026-05-30',
            status='PENDING'
        )
    """

    STATUS_CHOICES = (
        ('PENDING', _('Pending - Newly stashed entry, awaiting financial auditor review clearance')),
        ('APPROVED', _('Approved - Budget verified and locked, awaiting physical bank or cash box release')),
        ('REJECTED', _('Rejected - Auditing denied by management, execution pipeline aborted')),
        ('PAID', _('Paid - Cash out successfully completed, bank voucher finalized and closed')),
    )

    # Using BigAutoField matches BIGSERIAL primary key target requirements
    id = models.BigAutoField(primary_key=True)
    
    # ========================================================================
    # RELATIONSHIPS & MULTI-TENANCY
    # ========================================================================
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,  # Matches ON DELETE CASCADE from requirement
        default=1,
        related_name='expenses',
        db_index=True,
        help_text='Tenant corporate node owning and financing this commercial outlay row',
        db_comment='Multi-tenancy tenant reference'
    )
    
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,  # Production safety: strict PROTECT prevents breaking account books if a category is altered
        related_name='expenses',
        db_index=True,
        help_text='The specialized financial account category code grouping this type of cost outlay',
        db_comment='Strict reference targeting parent financial catalog node'
    )
    
    # ========================================================================
    # MULTI-DIMENSIONAL COST MATRIX LOGISTICS POINTERS
    # ========================================================================
    
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,  # Matches REFERENCES vehicles(id) ON DELETE SET NULL
        related_name='expenses',
        null=True,
        blank=True,
        db_index=True,
        help_text='The target fleet vehicle profile consuming this cash resource (e.g., fuel, tires, repairs)',
        db_comment='Soft reference mapping target fleet asset model'
    )
    
    trip = models.ForeignKey(
        Trip,
        on_delete=models.SET_NULL,  # Matches REFERENCES trips(id) ON DELETE SET NULL
        related_name='expenses',
        null=True,
        blank=True,
        db_index=True,
        help_text='The operational route trip execution context where this cost was generated (e.g., bridge toll fees)',
        db_comment='Soft reference mapping operational trip document instance'
    )
    
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,  # Matches REFERENCES branches(id) ON DELETE SET NULL
        related_name='expenses',
        null=True,
        blank=True,
        db_index=True,
        help_text='The corporate physical branch office or office station responsible for incurring this liability',
        db_comment='Soft reference mapping organizational facility division node'
    )
    
    employee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,  # Matches REFERENCES employees(id) ON DELETE SET NULL
        related_name='expenses',
        null=True,
        blank=True,
        db_index=True,
        help_text='The staff member or operational driver to whom this expenditure cash allocation is credited',
        db_comment='Soft reference mapping corporate human resource profile'
    )
    
    # ========================================================================
    # AUDIT TRAIL PERSONNEL PATHS
    # ========================================================================
    
    submitted_by = models.ForeignKey(
        UserAccount,
        on_delete=models.SET_NULL,  # Matches REFERENCES user_accounts(id) ON DELETE SET NULL
        related_name='submitted_expenses',
        null=True,
        blank=True,
        db_index=True,
        help_text='The internal operator user account or accounting assistant filing this invoice data row into storage',
        db_comment='Soft reference tracking initializing entry operator user'
    )
    
    approved_by = models.ForeignKey(
        UserAccount,
        on_delete=models.SET_NULL,  # Matches REFERENCES user_accounts(id) ON DELETE SET NULL
        related_name='approved_expenses',
        null=True,
        blank=True,
        db_index=True,
        help_text='The chief accountant or regional financial executive approving or rejecting this budget payout request',
        db_comment='Soft reference tracking authorizing executive user'
    )
    
    # ========================================================================
    # CORE METADATA VALUES & MONETARY REGISTER
    # ========================================================================
    
    title = models.CharField(
        max_length=255,  # Matches VARCHAR(255) NOT NULL
        help_text='Short human-readable summary name identifying this expense (e.g., 50L Oil Topup Plate 30K-9999)',
        db_comment='Public ledger title line descriptor summary text'
    )
    
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,  # Matches NUMERIC(15,2) NOT NULL
        validators=[MinValueValidator(0.01)],
        help_text='The exact mathematical total cash volume spent or requested for this specific line item voucher',
        db_comment='Absolute outbound commercial financial cash weight currency value balance'
    )
    
    expense_date = models.DateField(
        db_index=True,  # Critical optimization for generating chronological income/expense monthly balance reports
        help_text='The real-world business calendar date when the money was spent or when the physical invoice receipt was printed',
        db_comment='Real-world operational accounting transaction calendar date'
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        help_text='Granular descriptive annotations or breakdown justifications clarifying specific line parameters',
        db_comment='Administrative auditing textual log annotations'
    )
    
    attachment = models.CharField(
        max_length=500,  # Matches VARCHAR(500)
        null=True,
        blank=True,
        help_text='Cloud storage object URL or server location path pointing to scanned PDF invoices or picture receipts',
        db_comment='Cloud storage document asset URL string tracking token'
    )
    
    # ========================================================================
    # WORKFLOW CONTROL PROGRESSIONS & CHRONOLOGY
    # ========================================================================
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',  # Matches NOT NULL DEFAULT 'PENDING'
        db_index=True,
        help_text='The structural processing stage tracking this cost through auditing and layout payment lifecycles',
        db_comment='Workflow compliance tracking status taxonomy string token'
    )
    
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timezone-aware timestamp logging exactly when an authorized executive approved or rejected this file',
        db_comment='Management audit confirmation authorization timestamp'
    )
    
    created_at = models.DateTimeField(
        default=models.functions.Now,  # Matches NOT NULL DEFAULT NOW() at db compiler layer
        help_text='System record logging anchor tracking exactly when this entry row was stashed in the main DB',
        db_comment='Creation initialization timestamp'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp tracking exactly when parameter attributes inside this financial voucher node mutated',
        db_comment='Last database row tracking mutation modification timestamp'
    )

    class Meta:
        db_table = 'expenses'
        verbose_name = _('Corporate Expense Voucher')
        verbose_name_plural = _('Corporate Expense Vouchers')
        
        # Chronological accounting balance sheets prioritize descending date sort pipelines
        ordering = ['-expense_date', '-created_at']
        
        # ====================================================================
        # CONSTRAINTS & COMPOSITE LOCK INDEXES
        # ====================================================================
        
        constraints = [
            # Direct database-level CHECK constraint enforcing workflow state taxonomy compliance
            models.CheckConstraint(
                check=models.Q(status__in=['PENDING', 'APPROVED', 'REJECTED', 'PAID']),
                name='chk_expense_status_rules'
            ),
            # Target security check: Monetary registers cannot capture absolute negative values
            models.CheckConstraint(
                check=models.Q(amount__gt=0),
                name='chk_expense_amount_positive'
            )
        ]

    def __str__(self):
        """String representation"""
        return f"Expense #{self.id} | {self.title} (-{self.amount:,.0f} VND) [{self.status}]"

    # ========================================================================
    # PRODUCTION FINANCIAL STATE MACHINE WORKFLOWS
    # ========================================================================

    def clean(self):
        """
        Application-layer validation auditing financial business rules prior to ledger commit.
        """
        super().clean()
        
        # 1. Multi-Tenant Protection: Verify cross-leaks on nested master entities
        if self.category_id and self.tenant_id != self.category.tenant_id:
            raise ValidationError({
                'category': _('Cross-Tenant Data Leak Error: Target expense category catalog configuration belongs to a different tenant.')
            })
            
        # 2. Context Isolation Check: Ensure that a voucher has at least one directional cost object anchor
        if not any([self.vehicle_id, self.trip_id, self.branch_id, self.employee_id]):
            raise ValidationError(
                _('Accounting Rule Violation: An expense entry voucher must be anchored to at least one cost target entity (Vehicle, Trip, Branch, or Employee).')
            )
            
        # 3. Execution State Safeguard: Verify user authorization states match workflow requirements
        if self.status in ['APPROVED', 'PAID', 'REJECTED'] and not self.approved_by:
            raise ValidationError({
                'approved_by': _('Audit Failure: Moving a financial voucher out of PENDING requires a designated approving auditor user.')
            })

    def execute_approval(self, manager_user, set_approved=True):
        """
        Safely transitions an expense sheet through the managerial gatekeeper stage.
        
        Args:
            manager_user: UserAccount model instance tracking the authorized executive auditor
            set_approved: Boolean toggle. If False, converts row into a REJECTED state log line.
        """
        if self.status != 'PENDING':
            raise ValidationError(_("Workflow Exception: Only PENDING expense sheets are eligible for review evaluation steps."))
            
        from django.utils import timezone
        
        self.approved_by = manager_user
        self.approved_at = timezone.now()
        self.status = 'APPROVED' if set_approved else 'REJECTED'
        
        self.save(update_fields=['status', 'approved_by', 'approved_at', 'updated_at'])

    def execute_final_payout(self):
        """
        Locks the sheet into a closed PAID state. Triggered upon cash desk disbursement 
        or confirmation of bank wire clearing hooks.
        """
        if self.status != 'APPROVED':
            raise ValidationError(_("Financial Exception: Payout release requires the sheet to sit under an APPROVED state phase first."))
            
        self.status = 'PAID'
        self.save(update_fields=['status', 'updated_at'])