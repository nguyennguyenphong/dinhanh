# ============================================================================
# FILE: apps/customers/models.py
# Customer CRM & Loyalty Matrix Management Models
# ============================================================================

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db.models import Q

# Assuming this model exists in your production architecture
from tenants.models.tenants import Tenant


class Customer(models.Model):
    """
    Customer model managing passenger CRM profiles, loyalty matrices, and registration funnels.
    
    Features:
    - Multi-tenancy: Securely partitioned and isolated via tenant_id
    - Alphanumeric UUID Token: Universal immutable identifier generated via UUIDv4 structure
    - Loyalty Ledger Ecosystem: Tracks retention points combined with dynamic progression tiers
    - Multi-Channel Ingestion: Maps registration funnels from physical nodes to web booking integrations
    - Unique Constraint: Limits unique phone string registration to exactly once per specific corporate tenant scope
    
    Tiers:
    - STANDARD: Initial entry point tier baseline configuration
    - SILVER: Intermediate retention profile status, low-tier discount eligibility
    - GOLD: High-value frequent rider asset profile, priority seat preferences unlocked
    - PLATINUM: Elite corporate tier status, top-tier executive lounge or premium booking options
    
    Sources:
    - COUNTER: Registered physically at a ticketing office hub or terminal counter station
    - ONLINE: Ingested via consumer web application pipelines or mobile booking applications
    - AGENT: Provisioned by an authorized third-party business affiliate or agency terminal
    - IMPORT: Bulk migrated via legacy CRM databases or administrative spreadsheet uploads
    
    Example:
        # Create a new loyalty passenger profile
        vip_customer = Customer.objects.create(
            tenant_id=1,
            full_name='Nguyen Van A',
            phone='+84909123456',
            email='nguyenvana@gmail.com',
            tier='GOLD',
            source='ONLINE'
        )
    """

    TIER_CHOICES = (
        ('STANDARD', _('Standard - Entry baseline customer level')),
        ('SILVER', _('Silver - Intermediate tier level')),
        ('GOLD', _('Gold - High-value frequent rider level')),
        ('PLATINUM', _('Platinum - Premium elite status level')),
    )

    SOURCE_CHOICES = (
        ('COUNTER', _('Counter - Offline terminal ticket counter registration')),
        ('ONLINE', _('Online - Consumer web or mobile application portal')),
        ('AGENT', _('Agent - Third-party commercial travel agency system')),
        ('IMPORT', _('Import - Administrative spreadsheet or legacy DB data migration')),
    )

    id = models.BigAutoField(primary_key=True)
    
    # ========================================================================
    # RELATIONSHIPS & MULTI-TENANCY
    # ========================================================================
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,  # Matches ON DELETE CASCADE from requirement
        default=1,
        related_name='customers',
        db_index=True,
        help_text='Tenant owner who maintains ownership of this customer CRM identity profile',
        db_comment='Multi-tenancy tenant reference'
    )
    
    # ========================================================================
    # CORE IDENTIFIERS & SECURE TOKENS
    # ========================================================================
    
    # Matches UUID NOT NULL DEFAULT uuid_generate_v4() UNIQUE
    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        help_text='Global immutable UUIDv4 identifier string optimized for external API exposure frameworks',
        db_comment='Cryptographically secure unique identity token'
    )
    
    full_name = models.CharField(
        max_length=255,
        help_text='The full legal name coordinates of the passenger customer',
        db_comment='Customer legal full name text'
    )
    
    phone = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?[0-9\s\-]{7,20}$',
                message='Phone number format specification is invalid'
            )
        ],
        help_text='The primary contact mobile phone string sequence used for transaction and authentication logs',
        db_comment='Primary communication phone sequence'
    )
    
    # ========================================================================
    # DEMOGRAPHIC METADATA METRICS
    # ========================================================================
    
    email = models.EmailField(
        max_length=254,  # Matches max_length=254 adhering to standard email specifications
        null=True,
        blank=True,
        help_text='Electronic mail endpoint reference utilized for dynamic receipt or ticket issuance dispatches',
        db_comment='Electronic communication mail address node'
    )
    
    national_id = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text='Government issued asset identity validation parameters (e.g., Citizen ID, Passport number)',
        db_comment='Government statutory identity verification key token'
    )
    
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text='Calendar birth date marker utilized in age-group price classification algorithms',
        db_comment='Passenger birth calendar date marker'
    )
    
    gender = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text='Demographic taxonomy identification context gender indicator metadata',
        db_comment='Demographic gender metadata string description'
    )
    
    address = models.TextField(
        null=True,
        blank=True,
        help_text='The formal dynamic physical localized living residence reference context text',
        db_comment='Physical home address directory block text'
    )
    
    # ========================================================================
    # RETENTION LOYALTY LEDGER SYSTEMS
    # ========================================================================
    
    loyalty_points = models.IntegerField(
        default=0,
        help_text='Cumulative arithmetic currency ledger balance accumulated through successful corporate booking cycles',
        db_comment='Loyalty reward metrics ledger calculation point balance'
    )
    
    tier = models.CharField(
        max_length=20,
        choices=TIER_CHOICES,
        default='STANDARD',
        db_index=True,
        help_text='The classification segmentation tier evaluating customer priority metrics ranking matrices',
        db_comment='Loyalty matrix classification membership status index token'
    )
    
    # ========================================================================
    # MARKETING FUNNELS & DATA SOURCE INGESTIONS
    # ========================================================================
    
    source = models.CharField(
        max_length=30,
        choices=SOURCE_CHOICES,
        default='COUNTER',
        db_index=True,
        help_text='The primary customer onboarding ingestion origin channel context metric token',
        db_comment='Marketing CRM ingestion funnel system entry tag'
    )
    
    notes = models.TextField(
        null=True,
        blank=True,
        help_text='Miscellaneous service notes, wheelchair requirements, allergy alerts, or loyalty exemptions log',
        db_comment='Administrative CRM profiling text log annotations'
    )
    
    # ========================================================================
    # SYSTEM AUDITS
    # ========================================================================
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Timestamp when this customer registration entry card was formally opened inside the architecture CRM',
        db_comment='Creation timestamp'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp when parameters inside this customer account profile were last modified',
        db_comment='Last modification timestamp'
    )

    class Meta:
        db_table = 'customers'
        verbose_name = _('Customer Profile')
        verbose_name_plural = _('Customer Profiles')
        ordering = ['-created_at', 'full_name']
        
        # ====================================================================
        # CONSTRAINTS
        # ====================================================================
        
        constraints = [
            # Limits phone replication uniqueness under a single tenant scope (Matches UNIQUE (tenant_id, phone))
            models.UniqueConstraint(
                fields=['tenant', 'phone'],
                name='unique_tenant_customer_phone'
            ),
            # Direct database-level CHECK constraints for structural data integrity parameters
            models.CheckConstraint(
                check=models.Q(tier__in=['STANDARD', 'SILVER', 'GOLD', 'PLATINUM']),
                name='chk_customer_loyalty_tier'
            ),
            models.CheckConstraint(
                check=models.Q(source__in=['COUNTER', 'ONLINE', 'AGENT', 'IMPORT']),
                name='chk_customer_ingestion_source'
            ),
            models.CheckConstraint(
                check=models.Q(loyalty_points__gte=0),
                name='chk_customer_loyalty_points_positive'
            )
        ]
        
        # ====================================================================
        # INDEXES
        # ====================================================================
        
        indexes = [
            # Composite index optimized for CRM dashboards searching active phone contacts or name keywords matching tiers
            models.Index(
                fields=['tenant', 'tier', 'full_name'],
                name='idx_crm_tenant_tier_search',
                db_comment='Optimize marketing campaign segment filter queries'
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.full_name} ({self.phone}) - {self.tier}"

    # ========================================================================
    # CRM BUSINESS ENGINE & LOYALTY METHOD PROCESSORS
    # ========================================================================

    def clean(self):
        """
        Application-layer validation checking compliance parameters prior to model serialization.
        """
        super().clean()
        
        if self.loyalty_points and self.loyalty_points < 0:
            raise ValidationError({
                'loyalty_points': _('Loyalty metrics error: The wallet account point scale cannot reflect negative parameters.')
            })
            
        if self.email:
            self.email = self.email.strip().lower()

    def add_loyalty_rewards(self, earned_points, audit_log_reason=""):
        """
        Safely increment loyalty reward balances and evaluate pipeline structural tier promotion thresholds.
        
        Args:
            earned_points: Integer scalar value
            audit_log_reason: String reason note text
        """
        if earned_points <= 0:
            return
            
        self.loyalty_points += earned_points
        
        # Automatic Tier Advancement Matrix Rules Engine
        if self.loyalty_points >= 10000:
            self.tier = 'PLATINUM'
        elif self.loyalty_points >= 5000:
            self.tier = 'GOLD'
        elif self.loyalty_points >= 2000:
            self.tier = 'SILVER'
            
        # Append transactional tracing statements to internal notes log sheets
        append_note = f"[Points Added]: +{earned_points} pts | Reason: {audit_log_reason or 'Trip completion compensation reward'}"
        self.notes = f"{self.notes}\n{append_note}" if self.notes else append_note
        
        self.save(update_fields=['loyalty_points', 'tier', 'notes', 'updated_at'])

    def deduce_loyalty_rewards(self, spent_points, audit_log_reason):
        """
        Deduct points from ledger balance when client burns loyalty values during discount checkout ticket exchanges.
        
        Args:
            spent_points: Integer scalar value
            audit_log_reason: String reason note text
        """
        if spent_points <= 0:
            return
            
        if self.loyalty_points < spent_points:
            raise ValidationError(_("Insufficient loyalty balance coordinates available to perform the requested extraction code."))
            
        self.loyalty_points -= spent_points
        
        append_note = f"[Points Redeemed]: -{spent_points} pts | Reason: {audit_log_reason}"
        self.notes = f"{self.notes}\n{append_note}" if self.notes else append_note
        
        self.save(update_fields=['loyalty_points', 'notes', 'updated_at'])