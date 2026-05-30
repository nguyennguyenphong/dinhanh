# ============================================================================
# FILE: apps/customers/models.py
# Customer Loyalty Programs & Points Ledger Models
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

# Assuming these models exist in your production architecture
from customers_tickets.models.customers import Customer
from customers_tickets.models.ticket_bookings import TicketBooking


class LoyaltyTransaction(models.Model):
    """
    LoyaltyTransaction model acting as an immutable financial ledger tracking customer membership points.
    
    Features:
    - High-Fidelity Audit Ledger: Tracks incremental shifts and snapshot balances directly linked to customer profiles.
    - Contextual Order Linkage: Maps points velocity back to the generating ticket purchase (or NULL if non-booking event).
    - Signed Point Vector Intersections: Computes positive gains or negative reductions based on transactional modes.
    - Live Balance Auditing: Keeps a historic rolling account state record to prevent asynchronous ledger corruption.
    
    Transaction Types:
    - EARN: Positive points accumulated from completing commercial journeys or high-value booking checkouts.
    - REDEEM: Negative points spent as a currency substitute to subtract costs from checkout grand totals.
    - EXPIRE: Automatic purge executing on points that outlived their contractual calendar validity windows.
    - ADJUST: Manual modification injections triggered by corporate customer service desks to resolve disputes.
    
    Example:
        # Commit an automated point accumulation event upon ticket payment clearing
        log = LoyaltyTransaction.objects.create(
            customer_id=4501,
            booking_id=992815,
            type='EARN',
            points=150,        # Gained 150 points
            balance=1420       # New running balance snapshot
        )
    """

    TYPE_CHOICES = (
        ('EARN', _('Earn - Points accumulated from booking purchases or marketing check-ins')),
        ('REDEEM', _('Redeem - Points liquidated as commercial cash credits during order checkouts')),
        ('EXPIRE', _('Expire - Unused points passing past chronological validity deadlines')),
        ('ADJUST', _('Adjust - Administrative balance adjustments handled by support staff agents')),
    )

    # Using BigAutoField matches BIGSERIAL primary key target requirements
    id = models.BigAutoField(primary_key=True)
    
    # ========================================================================
    # RELATIONSHIPS & DATA INTEGRITY CONNECTIONS
    # ========================================================================
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,  # Matches REFERENCES customers(id) ON DELETE CASCADE
        related_name='loyalty_transactions',
        db_index=True,
        help_text='The parent client identity account profile who owns this points transaction snapshot'
    )
    
    booking = models.ForeignKey(
        TicketBooking,
        on_delete=models.SET_NULL,  # Matches REFERENCES ticket_bookings(id) ON DELETE SET NULL
        related_name='loyalty_transactions',
        null=True,
        blank=True,
        db_index=True,
        help_text='The specific revenue order booking ticket that triggered this points event. Holds NULL for adjustments or expiries.'
    )
    
    # ========================================================================
    # QUANTITATIVE SCORE MATRIX METRICS
    # ========================================================================
    
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        db_index=True,
        help_text='The dynamic action vector classification tracking the direction of this point mutation entry'
    )
    
    points = models.IntegerField(
        help_text='The absolute value magnitude of points shifted in this event. Can hold negative values for deductions.'
    )
    
    balance = models.IntegerField(
        help_text='The historical running snapshot balance total remaining inside the customer wallet immediately post-transaction'
    )
    
    # ========================================================================
    # METADATA LOGS & CHRONOLOGY
    # ========================================================================
    
    description = models.TextField(
        null=True,
        blank=True,
        help_text='Detailed textual ledger notes specifying why this change triggered (e.g., Earned from Trip Hanoi-Haiphong)'
    )
    
    created_at = models.DateTimeField(
        default=models.functions.Now,  # Matches NOT NULL DEFAULT NOW() at compilation layers
        help_text='Timezone-aware timestamp logging exactly when this point entry row committed into storage blocks'
    )

    class Meta:
        db_table = 'loyalty_transactions'
        verbose_name = _('Loyalty Points Transaction')
        verbose_name_plural = _('Loyalty Points Transactions')
        ordering = ['-created_at', '-id']
        
        # ====================================================================
        # CONSTRAINTS & COMPOSITE LOCK INDEXES
        # ====================================================================
        
        constraints = [
            # Direct database-level CHECK constraint enforcing point action taxonomy compliance
            models.CheckConstraint(
                condition=models.Q(type__in=['EARN', 'REDEEM', 'EXPIRE', 'ADJUST']),
                name='chk_loyalty_transaction_type_rules'
            ),
            # Verification check: The running balance pool total can never mathematically sit in negative values
            models.CheckConstraint(
                condition=models.Q(balance__gte=0),
                name='chk_loyalty_wallet_balance_positive'
            )
        ]

    def __str__(self):
        """String representation"""
        sign = "+" if self.points >= 0 else ""
        return f"Cust #{self.customer_id} | {self.type} ({sign}{self.points}) -> New Bal: {self.balance}"

    # ========================================================================
    # HIGH-INTEGRITY CONCURRENCY AUDITING & BALANCE VALIDATION MATHEMATICS
    # ========================================================================

    def clean(self):
        """
        Application-layer structural rules auditing vector orientations before locking data.
        """
        super().clean()
        
        # 1. Verification Gate: Enforce correct alignment between Transaction Type and Points Sign Vector
        if self.type == 'EARN' and self.points < 0:
            raise ValidationError({
                'points': _("Ledger Conflict: Accumulation operations ('EARN') cannot mathematically execute negative point values.")
            })
            
        if self.type == 'REDEEM' and self.points > 0:
            raise ValidationError({
                'points': _("Ledger Conflict: Cash credit redemptions ('REDEEM') must reflect negative math deductions inside the points column.")
            })
            
        if self.type == 'EXPIRE' and self.points > 0:
            raise ValidationError({
                'points': _("Ledger Conflict: Points expiration events ('EXPIRE') must reflect negative math deductions inside the points column.")
            })

    def save(self, *args, **kwargs):
        """
        Overridden save execution deploying atomicity locks on parent customer wallets 
        to calculate running balances and prevent double-spending anomalies.
        """
        self.full_clean()
        is_creating = self._state.adding
        
        if is_creating:
            # Production Engine Security Block: Use PostgreSQL row-level locks (SELECT FOR UPDATE) 
            # on the parent Customer model to prevent race condition corruption under massive concurrent traffic
            from django.db import transaction
            
            with transaction.atomic():
                # Lock parent record to pull a high-fidelity point balance checkpoint
                customer_profile = Customer.objects.select_for_update().get(pk=self.customer_id)
                
                # If fields aren't initialized yet, default to zero database space bounds
                current_loyalty_balance = getattr(customer_profile, 'loyalty_points', 0)
                
                # Compute the targeted downstream balance matrix node
                computed_balance = current_loyalty_balance + self.points
                
                if computed_balance < 0:
                    raise ValidationError(_("Wallet Starvation Exception: Operation denied. Customer points balance fails to clear zero bounds."))
                
                # Stash calculated snapshot weights directly onto our row entry
                self.balance = computed_balance
                super().save(*args, **kwargs)
                
                # Sync and commit updated cache stats directly back down onto parent core accounts
                customer_profile.loyalty_points = computed_balance
                customer_profile.save(update_fields=['loyalty_points', 'updated_at'])
        else:
            # Production Safety Guard: Immutable Ledger Pattern 
            # Block administrative updates to historical point rows to ensure audit sheet permanence
            raise ValidationError(_("Ledger Lock Exception: Historical points entries are immutable and cannot be updated."))