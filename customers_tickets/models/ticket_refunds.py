# ============================================================================
# FILE: apps/bookings/models.py
# Ticket Financial Refund Ledger Models
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db.models import Q

# Assuming these models exist in your production architecture
from customers_tickets.models.tickets import Ticket
from accounts.models.user_accounts import UserAccount  # Custom user model


class TicketRefund(models.Model):
    """
    TicketRefund model acting as the commercial financial accounting ledger for passenger ticket voids.
    
    Features:
    - Audit Trail Sign-off: Enforces dual-control approval pipelines (processed_by & approved_by markers)
    - Alphanumeric Refund Code: Enforces system-wide unique lookup voucher index tokens
    - Financial Deductions Engine: Tracks original balances, penalties, and computed net liquidations
    - Multi-Channel Payout Matrix: Maps outbound capital settlements back to distinct banking types
    
    Refund Methods:
    - CASH: Hard currency returned directly via physical station ticketing counter drawers
    - BANK_TRANSFER: Bank wire reversal (e.g., Vietcombank, Techcombank) managed via ERP gateways
    - WALLET: Micro-payment API partner credit reversal (e.g., Momo, ZaloPay, ShopeePay)
    - CREDIT: In-app internal virtual voucher points credited back to Customer CRM wallets
    
    Statuses:
    - PENDING: Document initialized by counter staff, holding inventory release while awaiting audit
    - APPROVED: Supervisor cleared the liquidation request, payout queue triggered
    - COMPLETED: Capital successfully moved past gateway nodes, ledger line balanced and permanently locked
    - REJECTED: Request denied by supervisor auditing, ticket status restored back to active state
    
    Example:
        # Create a new processing refund document line
        refund_line = TicketRefund.objects.create(
            ticket_id=45120,
            refund_code='RFD-20260530-X892',
            reason='Passenger changed business schedule planning',
            original_amount=350000.00,
            penalty_amount=50000.00,
            refund_amount=300000.00,
            refund_method='BANK_TRANSFER',
            status='PENDING'
        )
    """

    REFUND_METHOD_CHOICES = (
        ('CASH', _('Cash - Handed directly at physical counter terminal drawers')),
        ('BANK_TRANSFER', _('Bank Transfer - Electronic wire reversal processing')),
        ('WALLET', _('Wallet - E-Wallet partner integration API gateway return')),
        ('CREDIT', _('Credit - Virtual internal wallet voucher points issued')),
    )

    STATUS_CHOICES = (
        ('PENDING', _('Pending - Review pipeline active, awaiting manager validation')),
        ('APPROVED', _('Approved - Clearance authorized, payout transactional task queued')),
        ('COMPLETED', _('Completed - Capital successfully transferred, ledger locked')),
        ('REJECTED', _('Rejected - Request declined, booking ticket restored to active status')),
    )

    # Using BigAutoField matches BIGSERIAL primary key target requirements
    id = models.BigAutoField(primary_key=True)
    
    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================
    
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.PROTECT,
        related_name='refund_records',
        db_index=True,
        help_text='The specific boarding pass ticket identity sheet being processed for liquidation'
    )
    
    processed_by = models.ForeignKey(
        UserAccount,
        on_delete=models.SET_NULL,
        related_name='initiated_refunds',
        null=True,
        blank=True,
        db_index=True,
        help_text='The staff accountant or agent counter employee who initiated this liquidation line'
    )
    
    approved_by = models.ForeignKey(
        UserAccount,
        on_delete=models.SET_NULL,
        related_name='authorized_refunds',
        null=True,
        blank=True,
        db_index=True,
        help_text='The supervisor or station manager validating and granting commercial clearance sign-off'
    )
    
    # ========================================================================
    # IDENTITY CODE & CONTEXT
    # ========================================================================
    
    refund_code = models.CharField(
        max_length=30,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9\-_]+$',
                message='Refund voucher code must contain only uppercase letters, numbers, hyphens, and underscores'
            )
        ],
        help_text='Unique commercial index token used for tracking outbound financial vouchers (e.g., REF-9921-X)'
    )
    
    reason = models.TextField(
        null=True,
        blank=True,
        help_text='Contextual justification annotations explaining why this specific ticket was voided'
    )
    
    # ========================================================================
    # FINANCIAL ARITHMETIC MATRICES
    # ========================================================================
    
    original_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text='The net collected revenue amount paid originally for the ticket seat line'
    )
    
    penalty_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        help_text='The cancellation administrative fee penalty deducted from the client balance based on timeline policies'
    )
    
    refund_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text='The exact ultimate payout capital cash sum returned back to the consumer (original_amount - penalty_amount)'
    )
    
    refund_method = models.CharField(
        max_length=30,
        choices=REFUND_METHOD_CHOICES,
        null=True,
        blank=True,
        db_index=True,
        help_text='The target liquidation path used to route the outgoing capital back to the customer'
    )
    
    # ========================================================================
    # WORKFLOW PROGRESSION LIFECYCLES
    # ========================================================================
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        db_index=True,
        help_text='The structural state mapping this liquidation voucher through review and payout channels'
    )
    
    # ========================================================================
    # CHRONOLOGY AUDIT MARKS
    # ========================================================================
    
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timezone-aware timestamp logging exactly when final completion or rejection was executed'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp when this financial refund ledger line was first registered inside the core database'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp when parameters inside this financial refund line were last modified'
    )

    class Meta:
        db_table = 'ticket_refunds'
        verbose_name = _('Ticket Refund Ledger')
        verbose_name_plural = _('Ticket Refund Ledgers')
        ordering = ['-created_at', 'refund_code']
        
        # ====================================================================
        # CONSTRAINTS
        # ====================================================================
        
        constraints = [
            # Direct database-level CHECK constraints ensuring structural token validation parameters
            models.CheckConstraint(
                check=models.Q(status__in=['PENDING', 'APPROVED', 'COMPLETED', 'REJECTED']),
                name='chk_refund_status_rules'
            ),
            # Financial data integrity logic confirmation checks
            models.CheckConstraint(
                check=models.Q(original_amount__gte=0) & models.Q(penalty_amount__gte=0) & models.Q(refund_amount__gte=0),
                name='chk_refund_amounts_positive'
            )
        ]

    def __str__(self):
        """String representation"""
        return f"[{self.refund_code}] -> Ticket #{self.ticket_id} | Refund: {self.refund_amount:,.0f} VND [{self.status}]"

    # ========================================================================
    # BUSINESS METRICS & DUAL CONTROL AUDIT METHODS
    # ========================================================================

    def clean(self):
        """
        Application-layer financial audit calculation validation rules prior to commits.
        """
        super().clean()
        
        # Mathematical integrity check: Prevent revenue calculation anomalies
        if self.original_amount is not None and self.penalty_amount is not None and self.refund_amount is not None:
            expected_payout = self.original_amount - self.penalty_amount
            if expected_payout < 0:
                expected_payout = 0
            if abs(self.refund_amount - expected_payout) > 0.01:
                raise ValidationError({
                    'refund_amount': _('Accounting Arithmetic Error: Refund payout must equal (original_amount - penalty_amount) calculation matrix.')
                })

    def execute_supervisor_approval(self, supervisor_user):
        """
        Dual-Control Core: Evaluates and grants authorized manager clearance to the payout document line.
        
        Args:
            supervisor_user: UserAccount model instance (Checker role signature)
        """
        if self.status != 'PENDING':
            raise ValidationError(_("Review Block: This refund line document has already bypassed its reviewable PENDING state."))
            
        if self.processed_by == supervisor_user:
            raise ValidationError(_("Compliance Fraud Block: The supervisor initiating the refund (Maker) cannot act as the approver (Checker)."))
            
        self.status = 'APPROVED'
        self.approved_by = supervisor_user
        self.save(update_fields=['status', 'approved_by', 'updated_at'])

    def execute_final_payout_completion(self):
        """
        Finalizes the ledger transaction line after capital has physically moved past gateways.
        Locks data parameters and safely switches the target ticket profile state to REFUNDED.
        """
        if self.status != 'APPROVED':
            raise ValidationError(_("Payout Processing Error: Payout cannot execute without prior supervisor APPROVED clearance marks."))
            
        from django.utils import timezone
        
        self.status = 'COMPLETED'
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'processed_at', 'updated_at'])
        
        # Cascade Side-Effect: Permanently switch target ticket status to REFUNDED and release bến bãi inventory
        self.ticket.status = 'REFUNDED'
        self.ticket.save(update_fields=['status', 'updated_at'])
        
        # Internal pipeline hook: If ticket was assigned to a physical seat asset, 
        # release the seat allocation maps here for active market booking resales.