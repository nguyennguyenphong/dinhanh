# ============================================================================
# FILE: apps/logistics/models.py
# Logistics Financial Reconciliation & COD Control Models
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

# Assuming these models exist in your production architecture
from consignments.models.consignments import Consignment
from accounts.models.user_accounts import UserAccount  # Custom user model


class CodReconciliation(models.Model):
    """
    CodReconciliation model tracking the accounting settlement cycle of Cash-on-Delivery (COD) funds.
    
    Features:
    - Tight Consignment Linkage: Binds directly to the parent parcel to monitor specific cash liabilities.
    - Audit Trail Personnel Tracking: Logs the explicit internal accountant user committing the bank payout.
    - State Machine Compliance: Enforces strict progressive workflow statuses from PENDING to CONFIRMED.
    - Precision Monetary Registers: Maps standard NUMERIC financial fields to prevent float round-off errors.
    
    Statuses:
    - PENDING: Cargo has been delivered and COD cash captured at destination, awaiting finance desk release.
    - TRANSFERRED: Accountant has generated the bank transfer ledger matrix or dispatched cash out to the sender.
    - CONFIRMED: Originating sender client confirmed receipt of funds, or banking API cleared the statement row.
    
    Example:
        # Create a settlement ticket once a cargo parcel is successfully delivered
        ticket = CodReconciliation.objects.create(
            consignment_id=102948,
            amount=1500000.00,  # 1.5M VND collected COD
            status='PENDING'
        )
    """

    STATUS_CHOICES = (
        ('PENDING', _('Pending - Cash collected at counter, awaiting accountant clearance approval')),
        ('TRANSFERRED', _('Transferred - Outbound bank dispatch executed, funds sent to parcel sender')),
        ('CONFIRMED', _('Confirmed - Client confirmed receipt or bank statement webhook matched successfully')),
    )

    id = models.AutoField(primary_key=True)
    
    # ========================================================================
    # RELATIONSHIPS & DATA INTEGRITY CONNECTIONS
    # ========================================================================
    
    consignment = models.ForeignKey(
        Consignment,
        on_delete=models.PROTECT,
        related_name='cod_reconciliations',
        db_index=True,
        help_text='The specific source parcel consignment document whose cash flow liability is managed here'
    )
    
    transferred_by = models.ForeignKey(
        UserAccount,
        on_delete=models.SET_NULL,
        related_name='processed_cod_settlements',
        null=True,
        blank=True,
        db_index=True,
        help_text='The financial staff user or accountant account who cleared the payout and signed the bank voucher'
    )
    
    # ========================================================================
    # MONETARY METRIC METADATA (NUMERIC 15,2)
    # ========================================================================
    
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text='The precise mathematical cash currency total amount to be paid back out to the parcel sender client'
    )
    
    # ========================================================================
    # WORKFLOW CONTROL PROGRESSIONS & LIFECYCLE
    # ========================================================================
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        db_index=True,
        help_text='The accounting audit phase tracking this cash settlement through clearance banking pipelines'
    )
    
    notes = models.TextField(
        null=True,
        blank=True,
        help_text='Bank transaction sequence hashes, account details, or manual tracking annotations for discrepancies'
    )
    
    # ========================================================================
    # CHRONOLOGY WINDOWS
    # ========================================================================
    
    transferred_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timezone-aware timestamp logging exactly when the bank transfer API or cash desk pushed out the money'
    )
    
    created_at = models.DateTimeField(
        default=models.functions.Now,
        help_text='System record logging anchor tracking exactly when this reconciliation row was opened inside the core DB'
    )

    class Meta:
        db_table = 'cod_reconciliations'
        verbose_name = _('COD Cash Reconciliation')
        verbose_name_plural = _('COD Cash Reconciliations')
        ordering = ['-created_at', 'status']
        
        # ====================================================================
        # CONSTRAINTS
        # ====================================================================
        
        constraints = [
            # Direct database-level CHECK constraint enforcing workflow state taxonomy compliance
            models.CheckConstraint(
                condition=models.Q(status__in=['PENDING', 'TRANSFERRED', 'CONFIRMED']),
                name='chk_cod_reconciliation_status_rules'
            ),
            # Verification check: Monetary settlement metrics must reside in positive non-zero bounds
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name='chk_cod_reconciliation_amount_positive'
            )
        ]

    def __str__(self):
        """String representation"""
        return f"COD Recon #{self.id} [Consignment: {self.consignment_id}] Amt: {self.amount:,.0f} VND ({self.status})"

    # ========================================================================
    # ENTERPRISE LOGISTICS FINANCIAL OPERATIONS & BANKING STATE MACHINERY
    # ========================================================================

    def clean(self):
        """
        Application-layer validation auditing data integrity parameters prior to DB serialization locks.
        """
        super().clean()
        
        # Cross-model compliance rule: Prevent creating a reconciliation if the original consignment did not ask for COD
        if self.consignment_id and self.consignment.cod_amount <= 0:
            raise ValidationError({
                'consignment': _("Compliance Error: The linked cargo parcel does not possess a registered cash-on-delivery collection parameter.")
            })
            
        # Payout cross-check rule: Enforce consistency between amount and original cargo definition
        if self.consignment_id and self.amount and self.amount != self.consignment.cod_amount:
            raise ValidationError({
                'amount': _("Accounting Discrepancy: Payout allocation cannot deviate from the parent consignment's collected cod_amount.")
            })

    def execute_bank_transfer(self, accountant_user, transaction_reference_hash, custom_notes=""):
        """
        Dispatches and logs the initial financial payout from the company's central account.
        
        Args:
            accountant_user: UserAccount model instance tracking the authorized executive auditor
            transaction_reference_hash: String banking reference tracking token (e.g., FT2605309999)
            custom_notes: Optional text memo appending specific banking destination parameters
        """
        if self.status != 'PENDING':
            raise ValidationError(_("Financial Exception: Bank transfer execution requires a PENDING reconciliation leaf entry."))
            
        from django.utils import timezone
        
        self.status = 'TRANSFERRED'
        self.transferred_by = accountant_user
        self.transferred_at = timezone.now()
        
        # Format and secure transaction reference trace strings
        memo = f"[Bank Ref: {transaction_reference_hash}]"
        if custom_notes:
            memo += f" - {custom_notes}"
        self.notes = f"{self.notes}\n{memo}" if self.notes else memo
        
        self.save(update_fields=['status', 'transferred_by', 'transferred_at', 'notes'])
        
        # Cascade Automation Trigger: Update the parent consignment state to mirror financial workflow progression
        self.consignment.cod_transferred = True
        self.consignment.save(update_fields=['cod_transferred', 'updated_at'])

    def execute_final_clearance(self):
        """
        Confirms absolute completion of settlement. Triggered by client manual sign-off 
        or automatic reconciliation script checking bank Webhook responses.
        """
        if self.status != 'TRANSFERRED':
            raise ValidationError(_("Financial Exception: Clearance confirmation requests require the record to sit under a TRANSFERRED state phase."))
            
        self.status = 'CONFIRMED'
        self.save(update_fields=['status'])