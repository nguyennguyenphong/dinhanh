# ============================================================================
# FILE: apps/marketing/models.py
# Marketing Campaign & Promotional Coupon Models
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.contrib.postgres.fields import ArrayField  # Production feature required for Array data structures
from django.db.models import Q

# Assuming these models exist in your production architecture
from tenants.models.tenants import Tenant
from accounts.models.user_accounts import UserAccount  # Custom user model


class Promotion(models.Model):
    """
    Promotion model acting as the central coupon engine rule-sheet for discounting passenger fares.
    
    Features:
    - Multi-tenancy Isolation: Partitioned by tenant_id with localized unique code scopes.
    - Variable Discount Mechanics: Supports scaling reductions by percentage, flat currency amounts, or total complimentary seats.
    - Multi-Layered Anti-Drain Controls: Hard-caps cumulative campaign budgets and individual customer exploitation cycles.
    - Native PostgreSQL Array Filters: Targets specific routing graphs, seat classes, and sales distribution streams natively.
    
    Discount Types:
    - PERCENT: Decreases price by a floating scale factor (e.g., 10.00% off), bound by max_discount rules.
    - FIXED_AMOUNT: Deducts a static absolute currency voucher weight from gross cart totals (e.g., 50,000 VND off).
    - FREE_SEAT: Waives 100% of the single base inventory seat charge, ideal for corporate partnerships or marketing loyalty.
    
    Example:
        # Construct an active 10% flash-sale coupon bounded to specific online channels
        coupon = Promotion.objects.create(
            tenant_id=1,
            code='FLASHSALE26',
            name='Summer 2026 E-Gate Launch Promo',
            discount_type='PERCENT',
            discount_value=10.00,
            max_discount=50000.00,
            min_order_amount=200000.00,
            applicable_channels=['MOBILE_APP', 'WEB_PORTAL'],
            valid_from='2026-06-01T00:00:00Z',
            is_active=True
        )
    """

    DISCOUNT_TYPE_CHOICES = (
        ('PERCENT', _('Percentage - Scaled mathematical deduction bounded by max limits')),
        ('FIXED_AMOUNT', _('Fixed Amount - Absolute invariant commercial currency value deduction')),
        ('FREE_SEAT', _('Free Seat - Total asset valuation waiver for applied line units')),
    )

    id = models.AutoField(primary_key=True)
    
    # ========================================================================
    # RELATIONSHIPS & MULTI-TENANCY
    # ========================================================================
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,  # Matches ON DELETE CASCADE from requirement
        default=1,
        related_name='promotions',
        db_index=True,
        help_text='Tenant owner corporate node managing this isolated pricing coupon campaign leaf'
    )
    
    created_by = models.ForeignKey(
        UserAccount,
        on_delete=models.SET_NULL,  # Matches REFERENCES user_accounts(id) ON DELETE SET NULL
        related_name='created_promotions',
        null=True,
        blank=True,
        db_index=True,
        help_text='The specific internal marketing manager or administrator account who configured this coupon schema'
    )
    
    # ========================================================================
    # CORE IDENTITY METADATA
    # ========================================================================
    
    code = models.CharField(
        max_length=50,  # Matches VARCHAR(50) NOT NULL
        help_text='The alphanumeric string coupon key typed by passenger consumers at checkout panels (e.g., SUMMER26)'
    )
    
    name = models.CharField(
        max_length=255,  # Matches VARCHAR(255) NOT NULL
        help_text='Public human-readable campaign label text displayed across booking screens (e.g., Grand Opening Discount)'
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        help_text='Internal structural scope explanations or visible marketing terms and conditions rules text'
    )
    
    # ========================================================================
    # MATHEMATICAL REVENUE REDUCTION MATRICES
    # ========================================================================
    
    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,  # Enforces CONSTRAINT chk_promotion_type
        db_index=True,
        help_text='The algorithmic strategy chosen to compute transaction price deductions'
    )
    
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,  # Matches NUMERIC(10,2) NOT NULL
        validators=[MinValueValidator(0.00)],
        help_text='The active calculation metric magnitude multiplier. Represents percentages (e.g., 15.50) or absolute currencies (e.g., 50000.00)'
    )
    
    min_order_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,  # Matches NUMERIC(15,2)
        null=True,
        blank=True,
        validators=[MinValueValidator(0.00)],
        help_text='Minimum aggregate shopping cart invoice threshold required to trigger this calculation layout engine'
    )
    
    max_discount = models.DecimalField(
        max_digits=15,
        decimal_places=2,  # Matches NUMERIC(15,2)
        null=True,
        blank=True,
        validators=[MinValueValidator(0.00)],
        help_text='The structural ceiling safety limit preventing percentage-based deductions from draining excessive campaign funds'
    )
    
    # ========================================================================
    # RISK CONTROLS & USAGE LIMIT COUNTERS
    # ========================================================================
    
    usage_limit = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text='Total cumulative times this code can clear checkpoints system-wide across all consumers prior to exhaustion'
    )
    
    usage_limit_per_user = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text='Maximum allocation cycles a single unique client identity identity token can execute this specific code block'
    )
    
    usage_count = models.IntegerField(
        default=0,  # Matches NOT NULL DEFAULT 0
        validators=[MinValueValidator(0)],
        help_text='Live database increment index logging exactly how many times checkout checkouts successfully consumed this coupon line'
    )
    
    # ========================================================================
    # ADVANCED POSTGRESQL NATIVE ARRAY ROUTING FILTERS
    # ========================================================================
    
    applicable_routes = ArrayField(
        models.IntegerField(),
        null=True,
        blank=True,  # Matches INTEGER[] without NOT NULL constraint
        help_text='List arrays storing target Route database keys allowed to consume this coupon line. Empty arrays match ALL paths.'
    )
    
    applicable_seat_types = ArrayField(
        models.CharField(max_length=30),
        null=True,
        blank=True,  # Matches VARCHAR(30)[] without NOT NULL constraint
        help_text='List arrays storing distinct cabin classes eligible to request reductions (e.g., [VIP_SLEEPER, STANDARD_SEAT])'
    )
    
    applicable_channels = ArrayField(
        models.CharField(max_length=30),
        null=True,
        blank=True,  # Matches VARCHAR(30)[] without NOT NULL constraint
        help_text='List arrays restricting coupon activation to discrete sale gateways (e.g., [MOBILE_APP, B2B_AGENT, COUNTER_DESK])'
    )
    
    # ========================================================================
    # TIME WINDOWS, SWITCHES & CHRONOLOGY
    # ========================================================================
    
    valid_from = models.DateTimeField(
        help_text='Timezone-aware activation timeline node marking exactly when this coupon rule goes live online'
    )
    
    valid_to = models.DateTimeField(
        null=True,
        blank=True,  # Matches TIMESTAMPTZ without NOT NULL constraint
        help_text='Timezone-aware expiration date node marking exactly when this coupon ruleset automatically loses legal status'
    )
    
    is_active = models.BooleanField(
        default=True,  # Matches NOT NULL DEFAULT TRUE
        db_index=True,
        help_text='Master administrative toggle switch. Setting this false instantly blocks all checkout applications regardless of chronology rules'
    )
    
    created_at = models.DateTimeField(
        default=models.functions.Now,  # Matches NOT NULL DEFAULT NOW() at db layer
        help_text='System record logging anchor tracking exactly when this rule layout row entered the central database'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Timestamp tracking when parameters inside this promotional campaign node were last modified'
    )

    class Meta:
        db_table = 'promotions'
        verbose_name = _('Promotional Coupon')
        verbose_name_plural = _('Promotional Coupons')
        ordering = ['-created_at', 'code']
        
        # ====================================================================
        # CONSTRAINTS & UNIQUE MULTI-COLUMN INDEXES
        # ====================================================================
        
        constraints = [
            # Replicates exact structure of UNIQUE (tenant_id, code)
            models.UniqueConstraint(
                fields=['tenant', 'code'],
                name='uq_tenant_promotion_code'
            ),
            # Direct database-level CHECK constraint replicating CONSTRAINT chk_promotion_type
            models.CheckConstraint(
                condition=models.Q(discount_type__in=['PERCENT', 'FIXED_AMOUNT', 'FREE_SEAT']),
                name='chk_promotion_discount_type_enum'
            ),
            # Logical boundary constraints checking financial numeric safety parameters
            models.CheckConstraint(
                condition=models.Q(discount_value__gte=0) & models.Q(usage_count__gte=0),
                name='chk_promotion_metrics_positive'
            ),
            # Timeline security constraint: Opening dates must physically precede closing windows
            models.CheckConstraint(
                condition=models.Q(valid_to__gt=models.F('valid_from')) | models.Q(valid_to__isnull=True),
                name='chk_promotion_timeline_validity'
            )
        ]

    def __str__(self):
        """String representation"""
        return f"Tenant {self.tenant_id} - [{self.code}] {self.name} ({self.discount_type})"

    # ========================================================================
    # ALGORITHMIC PROMOTION CALCULATORS & BUSINESS LOGIC ENGINE
    # ========================================================================

    def clean(self):
        """
        Application-layer structural rules verification targeting marketing setups before commit.
        """
        super().clean()
        
        # 1. Validation logic for Date boundaries
        if self.valid_from and self.valid_to:
            if self.valid_from >= self.valid_to:
                raise ValidationError({
                    'valid_to': _('Campaign Error: Target expiration timestamp node must physically succeed activation valid_from landmarks.')
                })
                
        # 2. Mathematical safety check for percentage caps
        if self.discount_type == 'PERCENT':
            if self.discount_value > 100.00:
                raise ValidationError({
                    'discount_value': _('Financial Limit Error: Percentage-based calculations cannot mathematically scale above a 100.00% ceiling parameter.')
                })
            if not self.max_discount:
                # Production warning: Risk of extreme capital drain if high-value tickets are discounted without a cap
                pass

    def is_currently_valid(self, order_amount=0.00, sales_channel=None):
        """
        Comprehensive operational check determining if a customer checkout packet successfully 
        qualifies to apply this discount.
        
        Returns:
            Tuple (Boolean status, String message error if False)
        """
        from django.utils import timezone
        from decimal import Decimal
        
        now = timezone.now()
        
        # Gate A: Switch check
        if not self.is_active:
            return False, _("This promotional coupon has been administratively disabled.")
            
        # Gate B: Chronology boundary checks
        if now < self.valid_from:
            return False, _("This promotional coupon campaign has not reached its official activation date yet.")
        if self.valid_to and now > self.valid_to:
            return False, _("This promotional coupon code has reached its formal expiration date.")
            
        # Gate C: Exhaustion limits check
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False, _("This coupon allocation budget has been completely exhausted system-wide.")
            
        # Gate D: Cart baseline qualification check
        if self.min_order_amount and Decimal(str(order_amount)) < self.min_order_amount:
            return False, _(f"Cart value is below qualification benchmarks. Spend at least {self.min_order_amount:,.0f} VND to activate.")
            
        # Gate E: Distribution channel filter execution
        if self.applicable_channels and sales_channel and (sales_channel not in self.applicable_channels):
            return False, _("This promotional code is invalid for your chosen electronic sales gateway interface.")
            
        return True, "Success"

    def calculate_discount_reduction(self, base_fare_amount):
        """
        Calculates the exact monetary deduction weight for a given base ticket pricing point.
        
        Args:
            base_fare_amount: Decimal total pricing liability prior to coupon deduction
            
        Returns:
            Decimal (The calculated cash credit to subtract from invoice grand totals)
        """
        from decimal import Decimal
        
        fare = Decimal(str(base_fare_amount))
        if not self.is_active:
            return Decimal('0.00')
            
        if self.discount_type == 'FREE_SEAT':
            return fare
            
        elif self.discount_type == 'FIXED_AMOUNT':
            # Cap deduction at current fare bounds to prevent generating weird absolute negative cart states
            return min(self.discount_value, fare)
            
        elif self.discount_type == 'PERCENT':
            computed_drop = (fare * self.discount_value) / Decimal('100.00')
            if self.max_discount:
                return min(computed_drop, self.max_discount)
            return computed_drop
            
        return Decimal('0.00')