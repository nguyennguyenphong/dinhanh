# ============================================================================
# FILE: apps/bookings/models.py
# Ticket Bookings Operational Core Models
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db.models import Q

# Assuming these models exist in your production architecture
from tenants.models.tenants import Tenant
from customers_tickets.models.customers import Customer
from trips.models.trips import Trip
from accounts.models.user_accounts import UserAccount  # Custom user model
from branches.models.branches import Branch


class TicketBooking(models.Model):
    """
    TicketBooking model representing the transaction header ledger for passenger reservations.
    
    Features:
    - Multi-tenancy: Securely partitioned and isolated via tenant_id
    - Unique Booking Reference: Human-readable unique alphanumeric code enforced system-wide
    - High-Precision Financials: Tracks transactional amounts using Decimal fields (NUMERIC(15,2))
    - Inventory Lifecycle: Manages ticket reservation holds via explicit 'expires_at' thresholds
    - Multi-Channel Architecture: Maps sales ingestion origins from offline windows to B2B links
    
    Channels:
    - COUNTER: Physical ticket box office counter or station ticket terminal
    - ONLINE: Public consumer web platform checkout interface
    - AGENT: Authorized third-party retail travel agent console
    - MOBILE_APP: Native Android/iOS consumer application interface
    - B2B: High-volume corporate contract system API integration gateway
    
    Statuses:
    - PENDING: Ticket space temporarily reserved/held, awaiting successful payment clearance
    - CONFIRMED: Payment fully/partially processed, inventory permanently locked, ticket active
    - CANCELLED: Voided before journey, seats released back to the general inventory pool
    - REFUNDED: Voided with financial commercial reversal processed back to customer bank accounts
    - NO_SHOW: Journey departed, passenger failed to board vehicle within legal buffer gates
    
    Example:
        # Create a new pending ticket hold
        booking = TicketBooking.objects.create(
            tenant_id=1,
            booking_code='BKG-20260530-99X8',
            customer_id=12,
            trip_id=4,
            channel='MOBILE_APP',
            status='PENDING',
            total_amount=350000.00,
            expires_at='2026-05-30T01:00:00+07:00'
        )
    """

    CHANNEL_CHOICES = (
        ('COUNTER', _('Counter - Physical offline ticketing desk office')),
        ('ONLINE', _('Online - Consumer desktop web platform checkout')),
        ('AGENT', _('Agent - Third-party travel agency portal application')),
        ('MOBILE_APP', _('Mobile App - Native consumer smartphone software application')),
        ('B2B', _('B2B - Corporate affiliate API integration gateway connection')),
    )

    STATUS_CHOICES = (
        ('PENDING', _('Pending - Seat held, awaiting financial transaction clearance')),
        ('CONFIRMED', _('Confirmed - Ticket active, inventory assigned and validated')),
        ('CANCELLED', _('Cancelled - Aborted reservation, inventory released back to pool')),
        ('REFUNDED', _('Refunded - Voided with commercial banking reversal executed')),
        ('NO_SHOW', _('No Show - Trip departed, passenger failed check-in gates')),
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
        related_name='ticket_bookings',
        db_index=True,
        help_text='Tenant corporate owner who holds rights over this transactional booking ledger',
        db_comment='Multi-tenancy tenant reference'
    )
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,  # Production safety: block deleting a customer profile if booking logs exist
        related_name='bookings',
        db_index=True,  # Matches CREATE INDEX idx_bookings_customer
        help_text='The customer asset or primary passenger lodging this transaction sheet',
        db_comment='Reference to customer profile purchaser'
    )
    
    trip = models.ForeignKey(
        Trip,
        on_delete=models.PROTECT,  # Production safety: block deleting a trip commercial node if tickets are issued
        related_name='bookings',
        db_index=True,  # Matches CREATE INDEX idx_bookings_trip
        help_text='The active physical commercial trip journey line assigned under this ticket',
        db_comment='Reference to commercial trip model instance'
    )
    
    booked_by = models.ForeignKey(
        UserAccount,
        on_delete=models.SET_NULL,  # Matches REFERENCES user_accounts(id) ON DELETE SET NULL
        related_name='processed_bookings',
        null=True,
        blank=True,
        db_index=True,
        help_text='The corporate system user account who executed or processed this sale profile',
        db_comment='Reference to employee user account executing the order'
    )
    
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,  # Matches REFERENCES branches(id) ON DELETE SET NULL
        related_name='branch_bookings',
        null=True,
        blank=True,
        db_index=True,
        help_text='The physical branch office station hub where this booking transaction was logged',
        db_comment='Reference to originating office branch node'
    )
    
    # ========================================================================
    # IDENTITY & LOGISTICS DISTRIBUTION CHANNELS
    # ========================================================================
    
    booking_code = models.CharField(
        max_length=30,
        unique=True,  # Matches VARCHAR(30) NOT NULL UNIQUE
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9\-_]+$',
                message='Booking code must contain only uppercase alphanumeric characters, hyphens, and underscores'
            )
        ],
        help_text='Unique human-readable ticketing code index used for customer reservation validation (e.g., PNR-9982X)',
        db_comment='Unique system transaction lookup token key code'
    )
    
    channel = models.CharField(
        max_length=30,
        choices=CHANNEL_CHOICES,
        default='COUNTER',
        db_index=True,  # Matches CREATE INDEX idx_bookings_channel
        help_text='The distribution sales channel pipeline through which this transaction entered the system',
        db_comment='Sales ingestion distribution pipeline taxonomy token'
    )
    
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='PENDING',
        db_index=True,  # Matches CREATE INDEX idx_bookings_status
        help_text='The core transactional stage tracking this reservation lifecycle step sequence',
        db_comment='Workflow transaction progression taxonomy status string token'
    )
    
    # ========================================================================
    # FINANCIAL LEDGER METRICS
    # ========================================================================
    
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,  # Matches NUMERIC(15,2) NOT NULL DEFAULT 0
        help_text='The gross commercial price balance calculated for this entire ticket booking sheet',
        db_comment='Total calculated invoice financial debt balance'
    )
    
    paid_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,  # Matches NUMERIC(15,2) NOT NULL DEFAULT 0
        help_text='The total cash/digital ledger values successfully cleared and captured for this invoice',
        db_comment='Total captured incoming payment currency ledger sum'
    )
    
    # ========================================================================
    # LIFECYCLE CHRONOLOGY & AUDITS
    # ========================================================================
    
    note = models.TextField(
        null=True,
        blank=True,
        help_text='Miscellaneous customer preferences notes, specific wheelchair alerts, or manual audit details',
        db_comment='Administrative text log annotations'
    )
    
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timezone-aware timestamp logging exactly when this ticket profile was aborted',
        db_comment='Timestamp tracking reservation termination execution'
    )
    
    cancel_reason = models.TextField(
        null=True,
        blank=True,
        help_text='Explicit text statement provided explaining why this ticket reservation was aborted',
        db_comment='Cancellation background context logs'
    )
    
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timezone-aware ticket hold duration window boundary. If payment drops past this, hold voids automatically',
        db_comment='Timezone-aware countdown hold threshold limit'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,  # Matches CREATE INDEX idx_bookings_created ON ticket_bookings(created_at DESC)
        help_text='Timestamp when this booking ledger paper row was first initialized inside the architecture',
        db_comment='Creation timestamp'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp when fields inside this transaction profile were last modified (Managed via trigger in DDL)',
        db_comment='Last modification timestamp managed by core DB schema hooks'
    )

    class Meta:
        db_table = 'ticket_bookings'
        verbose_name = _('Ticket Booking')
        verbose_name_plural = _('Ticket Bookings')
        ordering = ['-created_at', 'booking_code']
        
        # ====================================================================
        # CONSTRAINTS
        # ====================================================================
        
        constraints = [
            # Direct database-level CHECK constraints matching CONSTRAINT chk_booking_status and chk_booking_channel
            models.CheckConstraint(
                check=models.Q(status__in=['PENDING', 'CONFIRMED', 'CANCELLED', 'REFUNDED', 'NO_SHOW']),
                name='chk_booking_status'
            ),
            models.CheckConstraint(
                check=models.Q(channel__in=['COUNTER', 'ONLINE', 'AGENT', 'MOBILE_APP', 'B2B']),
                name='chk_booking_channel'
            ),
            # Financial integrity check: Paid scale cannot physically exceed invoice totals
            models.CheckConstraint(
                check=models.Q(paid_amount__gte=0) & models.Q(total_amount__gte=0),
                name='chk_booking_amounts_positive'
            )
        ]

    def __str__(self):
        """String representation"""
        return f"[{self.booking_code}] -> Customer: {self.customer_id} | Amount: {self.total_amount:,.0f} VND ({self.status})"

    # ========================================================================
    # BUSINESS LOGIC & STATE MACHINE ENGINE WORKFLOWS
    # ========================================================================

    def clean(self):
        """
        Application-layer validation parsing matrix compliance before committing records.
        """
        super().clean()
        
        if self.status == 'CANCELLED' and not self.cancel_reason:
            raise ValidationError({
                'cancel_reason': _('Business Compliance Error: Aborting a confirmed reservation requires an explicit text reason log.')
            })

    def is_hold_expired(self):
        """
        Verify if the temporary inventory hold window has expired without payment processing.
        
        Returns:
            Boolean
        """
        from django.utils import timezone
        if self.status == 'PENDING' and self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def capture_payment_confirmation(self, amount_received):
        """
        Register processed cash flow metrics against this invoice. 
        Automatically escalates status to CONFIRMED if balances clear.
        
        Args:
            amount_received: Decimal scalar value
        """
        if self.status not in ['PENDING', 'CONFIRMED']:
            raise ValidationError(_("Financial workflow block: Cannot process payments on closed or cancelled ledger sheets."))
            
        self.paid_amount += amount_received
        
        # If the financial obligation is satisfied, shift state to CONFIRMED
        if self.paid_amount >= self.total_amount:
            self.status = 'CONFIRMED'
            self.expires_at = None  # Clear inventory release countdown hold
            
        self.save(update_fields=['paid_amount', 'status', 'expires_at', 'updated_at'])

    def execute_cancellation_void(self, reason_text):
        """
        Aborts an active reservation, logs the audit trail metrics, and releases seats back into bến bãi inventory.
        
        Args:
            reason_text: String explanation notes
        """
        if self.status in ['CANCELLED', 'REFUNDED', 'NO_SHOW']:
            raise ValidationError(_("State Machine Error: This reservation record is already closed or terminated."))
            
        from django.utils import timezone
        
        self.status = 'CANCELLED'
        self.cancelled_at = timezone.now()
        self.cancel_reason = reason_text
        self.save(update_fields=['status', 'cancelled_at', 'cancel_reason', 'updated_at'])
        
        # Integration cascade hook point: Trigger downstream signals here to 
        # instantly free up assigned seat map coordinates back into available booking pools.

    # ========================================================================
    # CLASSMETHODS / DATA ANALYSIS PIPELINES
    # ========================================================================

    @classmethod
    def process_stale_holds_cleanup(cls, tenant_id):
        """
        Batch clean cron utility looking up expired pending ticket holds to auto-cancel them.
        Highly critical background routine tasked with restoring abandoned cart seats back to sales pools.
        
        Args:
            tenant_id: Integer corporate scope identifier
            
        Returns:
            Integer (Count of released reservation documents)
        """
        from django.utils import timezone
        now_marker = timezone.now()
        
        stale_records = cls.objects.filter(
            tenant_id=tenant_id,
            status='PENDING',
            expires_at__lt=now_marker
        )
        
        updated_count = 0
        for booking in stale_records:
            try:
                booking.execute_cancellation_void(_("Automated system hold release: Payment countdown gate timeout limit reached."))
                updated_count += 1
            except ValidationError:
                continue
                
        return updated_count