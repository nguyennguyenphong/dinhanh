# ============================================================================
# FILE: apps/payments/models.py
# Cashier POS Session & Point of Sale Operations Models
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import Q

# Assuming these models exist in your production architecture
from tenants.models.tenants import Tenant
from accounts.models.user_accounts import UserAccount  # Custom user model
from branches.models.branches import Branch


class CashierSession(models.Model):
    """
    CashierSession model tracking the physical cash drawer life cycle at station ticket office nodes.
    
    Features:
    - Multi-tenancy Isolation: Securely partitioned and isolated via tenant_id
    - Strict Personnel Linking: Maps the explicit cashier employee and the originating physical branch office
    - Precision POS Reconciliation: Monitors cash flow metrics including start cash, end cash, sales, and refunds
    - Automated Discrepancy Auditing: Dynamically computes internal ledger variances against physical drawer counts
    
    Statuses:
    - OPEN: Active session shift, cashier is currently issuing tickets and capturing cash flow transactions
    - CLOSED: Drawer locked by employee, physical cash counted, awaiting management accounting audit
    - RECONCILED: Financial balance verified by finance managers, ledger line balanced and permanently locked
    
    Example:
        # Open a morning shift session for a counter cashier
        session = CashierSession.objects.create(
            tenant_id=1,
            cashier_id=14,
            branch_id=3,
            opening_cash=2000000.00,  # 2M VND float starting cash drawer
            status='OPEN'
        )
    """

    STATUS_CHOICES = (
        ('OPEN', _('Open - Active operational shift, capturing counter point-of-sale transactions')),
        ('CLOSED', _('Closed - Drawer locked, physical balance submitted, awaiting audit review')),
        ('RECONCILED', _('Reconciled - Audited by finance manager, variance cleared and ledger locked')),
    )

    id = models.AutoField(primary_key=True)
    
    # ========================================================================
    # RELATIONSHIPS & MULTI-TENANCY
    # ========================================================================
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,  # Matches ON DELETE CASCADE from requirement
        default=1,
        related_name='cashier_sessions',
        db_index=True,
        help_text='Tenant corporate owner who holds rights over this physical point-of-sale shift node'
    )
    
    cashier = models.ForeignKey(
        UserAccount,
        on_delete=models.PROTECT,  # Production safety: block deleting user if historical cash audit trails exist
        related_name='cashier_sessions',
        db_index=True,
        help_text='The employee user account assigned to manage the physical cash drawer during this shift window'
    )
    
    branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,  # Production safety: block deleting physical branch if accounting sessions refer to it
        related_name='cashier_sessions',
        db_index=True,
        help_text='The physical branch terminal hub or office location where the transaction drawer is operated'
    )
    
    # ========================================================================
    # CHRONOLOGY WINDOWS
    # ========================================================================
    
    opened_at = models.DateTimeField(
        default=models.functions.Now,  # Matches NOT NULL DEFAULT NOW() at execution layer
        db_index=True,
        help_text='Timezone-aware timestamp logging exactly when the cashier initialized the terminal drawer shift'
    )
    
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timezone-aware timestamp logging when the cashier declared the shift finished and locked access keys'
    )
    
    # ========================================================================
    # FINANCIAL LEDGER AUDIT MATRICES
    # ========================================================================
    
    opening_cash = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,  # Matches NUMERIC(15,2) NOT NULL DEFAULT 0
        help_text='The opening cash floating balance inside the terminal drawer drawer at shift start'
    )
    
    closing_cash = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,  # Matches NUMERIC(15,2) without default
        help_text='The actual physical cash asset total counted by the employee at the end of the shift duration'
    )
    
    total_sales = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='The calculated mathematical sum of all revenue-generating tickets processed during this session'
    )
    
    total_refunds = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='The calculated mathematical sum of all cash payouts refunded out from this drawer during the shift'
    )
    
    discrepancy = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='The calculated variance error metric (reported cash vs mathematically expected cash balance matrix)'
    )
    
    # ========================================================================
    # WORKFLOW PROGRESSION LIFECYCLES & ANNOTATIONS
    # ========================================================================
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='OPEN',
        db_index=True,
        help_text='The operational validation checkpoint phase tracking this cashier point-of-sale terminal sheet'
    )
    
    notes = models.TextField(
        null=True,
        blank=True,
        help_text='Explanations regarding cash drawer discrepancies, bank run delays, or unexpected power losses'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='System record logging anchor tracking exactly when this session index row was generated'
    )

    class Meta:
        db_table = 'cashier_sessions'
        verbose_name = _('Cashier POS Session')
        verbose_name_plural = _('Cashier POS Sessions')
        ordering = ['-opened_at', 'cashier']
        
        # ====================================================================
        # CONSTRAINTS
        # ====================================================================
        
        constraints = [
            # Direct database-level CHECK constraint enforcing workflow state taxonomy security
            models.CheckConstraint(
                condition=models.Q(status__in=['OPEN', 'CLOSED', 'RECONCILED']),
                name='chk_cashier_session_status_rules'
            ),
            # Verification check: Opening baseline financial data scales must sit in positive numbers bounds
            models.CheckConstraint(
                condition=models.Q(opening_cash__gte=0),
                name='chk_session_opening_cash_positive'
            )
        ]

    def __str__(self):
        """String representation"""
        return f"Session #{self.id} [Cashier: {self.cashier_id}] Branch: {self.branch_id} ({self.status})"

    # ========================================================================
    # POINT OF SALE SHIFT CONTROL & RECONCILED STATE MACHINE WORKFLOWS
    # ========================================================================

    def clean(self):
        """
        Application-layer integrity checks before database serialization locks.
        """
        super().clean()
        
        # Guard clause: Prevent employee from initiating negative starting float cash metrics
        if self.opening_cash and self.opening_cash < 0:
            raise ValidationError({'opening_cash': _('POS Compliance Error: Opening float cash values cannot reflect negative figures.')})

    def execute_shift_close(self, counted_physical_cash):
        """
        Closes an active cashier session shift. Accumulates real-time sales ledger 
        indexes, maps cash flows, and logs the calculated variance discrepancy metrics.
        
        Args:
            counted_physical_cash: Decimal scalar value representing the counted money inside the drawer
        """
        if self.status != 'OPEN':
            raise ValidationError(_("POS Shift Block: Shift termination can only execute on an ACTIVE OPEN cashier session."))
            
        from django.utils import timezone
        from django.db.models import Sum
        from payments.models.payments import Payment  # Dynamic relative cross-imports referencing
        
        # 1. Fetch and aggregate total point-of-sale invoice revenues captured by this cashier in cash
        # Filtering for payment method 'CASH' and status 'SUCCESS' under this specific shift window
        aggregated_sales = Payment.objects.filter(
            tenant=self.tenant,
            cashier=self.cashier,
            branch=self.branch,
            method__code='CASH',
            status='SUCCESS',
            created_at__gte=self.opened_at
        ).aggregate(sum_amount=Sum('amount'))['sum_amount'] or 0.00
        
        # 2. Fetch and aggregate total outbound counter ticket cash refunds disbursed from this drawer
        # Assuming an outbound refund system lookup matches similar operational parameters
        # For demonstration purposes, mock query pattern applies matching production designs:
        aggregated_refunds = 0.00  # Replace with appropriate query linkage when necessary
        
        # 3. Compute mathematically expected cash drawer balance metrics
        expected_cash_in_drawer = self.opening_cash + aggregated_sales - aggregated_refunds
        
        # 4. Compute structural accounting variance discrepancy metrics
        # discrepancy = Actual Counted Cash - Mathematically Expected System Ledger Cash
        calculated_discrepancy = counted_physical_cash - expected_cash_in_drawer
        
        # 5. Lock and freeze the operational database data parameters
        self.status = 'CLOSED'
        self.closed_at = timezone.now()
        self.closing_cash = counted_physical_cash
        self.total_sales = aggregated_sales
        self.total_refunds = aggregated_refunds
        self.discrepancy = calculated_discrepancy
        
        self.save(update_fields=[
            'status', 'closed_at', 'closing_cash', 'total_sales', 
            'total_refunds', 'discrepancy', 'updated_at'
        ])

    def execute_finance_reconciliation(self, auditor_user, manager_notes=""):
        """
        Allows auditing managers or senior accounting teams to sign off on closed shifts, 
        clearing discrepancies into company accounting journals and locking the record permanently.
        
        Args:
            auditor_user: UserAccount model instance tracking the authorized executive auditor
            manager_notes: Optional text string appending manager audit validation comments
        """
        if self.status != 'CLOSED':
            raise ValidationError(_("Auditing Block: Sessions must bypass terminal employee shift CLOSE before review clearance."))
            
        self.status = 'RECONCILED'
        if manager_notes:
            self.notes = f"{self.notes}\n[Audit Log - Managed by User #{auditor_user.id}]: {manager_notes}" if self.notes else f"[Audit Log]: {manager_notes}"
            
        self.save(update_fields=['status', 'notes', 'updated_at'])