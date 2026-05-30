# ============================================================================
# FILE: apps/marketing/models.py
# After-Sales Marketing & Customer Retention Models
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

# Assuming these models exist in your production architecture
from tenants.models.tenants import Tenant
from accounts.models.user_accounts import UserAccount  # Custom user model


class AfterSales(models.Model):
    """
    AfterSales model managing promotional reward rules triggered post-purchase to drive retention.
    
    Features:
    - Multi-tenancy Isolation: Securely partitioned via tenant_id with localized unique code enforcement.
    - Polymorphic Reward Structuring: Governs dynamic reward paths (Vouchers, Loyalty Points, Gifts, Discount Codes).
    - Schemaless Condition Processing: Leverages PostgreSQL JSONB validation to manage flexible trigger matrices 
      (e.g., minimum trips completed, specific routes traveled, historical milestone spend thresholds).
    - Audit Trail Assignment: Track the specific administrative officer initializing the corporate policy rulesheet.
    
    Reward Types:
    - VOUCHER: Generates a specific balance-backed prepaid electronic debit card for subsequent ticket payments.
    - LOYALTY_POINTS: Automatically injects an absolute point volume multiplier block straight into member wallets.
    - GIFT: Records physical corporate inventory claims (e.g., brand backpacks, travel pillows) issued at branch quầy counters.
    - DISCOUNT_CODE: Generates a distinct localized percent/flat coupon key restricted to the specific customer profile.
    
    Example:
        # Construct an active post-purchase rule gifting 500 loyalty points upon condition qualification
        policy = AfterSales.objects.create(
            tenant_id=1,
            code='POST_TRIP_BONUS_2026',
            name='First-Time Journey Completed Loyalty Grant',
            type='LOYALTY_POINTS',
            value=500.00,
            conditions={
                "trigger_event": "TRIP_COMPLETED",
                "min_completed_trips": 1,
                "target_customer_tier": "NEW_USER"
            },
            is_active=True
        )
    """

    TYPE_CHOICES = (
        ('VOUCHER', _('Voucher - High-fidelity electronic balance debit card generation')),
        ('LOYALTY_POINTS', _('Loyalty Points - Automated quantitative membership wallet point injections')),
        ('GIFT', _('Gift - Physical merchandise line item inventory claiming authorization')),
        ('DISCOUNT_CODE', _('Discount Code - Dynamic customized checkout promotional coupon generation')),
    )

    id = models.AutoField(primary_key=True)
    
    # ========================================================================
    # RELATIONSHIPS & MULTI-TENANCY
    # ========================================================================
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,  # Matches ON DELETE CASCADE from requirement
        default=1,
        related_name='after_sales_policies',
        db_index=True,
        help_text='Tenant corporate owner holding legal data sovereignty over this CRM retention campaign node'
    )
    
    created_by = models.ForeignKey(
        UserAccount,
        on_delete=models.SET_NULL,  # Matches REFERENCES user_accounts(id) ON DELETE SET NULL
        related_name='created_after_sales',
        null=True,
        blank=True,
        db_index=True,
        help_text='The authorized system administrator or marketing strategist user account who compiled this reward matrix'
    )
    
    # ========================================================================
    # CORE IDENTITY METADATA
    # ========================================================================
    
    code = models.CharField(
        max_length=50,  # Matches VARCHAR(50) NOT NULL
        help_text='The unique system text key code used to classify this retention policy rule (e.g., RETURN_USER_BONUS)'
    )
    
    name = models.CharField(
        max_length=255,  # Matches VARCHAR(255) NOT NULL
        help_text='Public or internal campaign title descriptive name text displayed in administrative panels'
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        help_text='Detailed descriptions capturing operational parameters, policy scopes, or audit notes'
    )
    
    # ========================================================================
    # QUANTITATIVE MAGNITUDES & TAXONOMY CLASSIFICATIONS
    # ========================================================================
    
    type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,  # Models the implicit ENUM requirement
        db_index=True,
        help_text='The primary rewarding strategy type framework deployed upon successful qualification check clears'
    )
    
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,  # Matches NUMERIC(10,2)
        null=True,
        blank=True,
        validators=[MinValueValidator(0.00)],
        help_text='The raw magnitude scale tracking reward values. Maps to cash weight balances, absolute point counts, or percentages.'
    )
    
    # ========================================================================
    # ADVANCED POSTGRESQL NATIVE SCHEMALESS JSONB TRIGGERS
    # ========================================================================
    
    conditions = models.JSONField(
        default=dict,  # Matches NOT NULL DEFAULT '{}' natively at database compiler layers
        help_text='Schemaless validation rule matrices mapping criteria fields (e.g., {"target_route_id": 5, "min_spend": 200000})'
    )
    
    # ========================================================================
    # CONTROL SWITCHES & CHRONOLOGY TIMESTAMPS
    # ========================================================================
    
    is_active = models.BooleanField(
        default=True,  # Matches NOT NULL DEFAULT TRUE
        db_index=True,
        help_text='Master state switch engine. Setting this False safely deactivates the automatic rule logic processing queues instantly'
    )
    
    created_at = models.DateTimeField(
        default=models.functions.Now,  # Matches NOT NULL DEFAULT NOW() at core DDL layers
        help_text='System record logging anchor tracking exactly when this rule layout row entered the main database'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,  # Matches default updated_at trigger requirements cleanly via application side hooks
        help_text='Timestamp tracking exactly when parameter attributes inside this after-sales configuration node mutated'
    )

    class Meta:
        db_table = 'after_sales'
        verbose_name = _('After-Sales Policy')
        verbose_name_plural = _('After-Sales Policies')
        ordering = ['-created_at', 'code']
        
        # ====================================================================
        # CONSTRAINTS & MULTI-COLUMN INDEX OVERRIDES
        # ====================================================================
        
        constraints = [
            # Direct database-level unique constraint matching UNIQUE (tenant_id, code)
            models.UniqueConstraint(
                fields=['tenant', 'code'],
                name='uq_tenant_after_sales_code'
            ),
            # Direct database-level CHECK constraint enforcing reward strategy taxonomy compliance
            models.CheckConstraint(
                check=models.Q(type__in=['VOUCHER', 'LOYALTY_POINTS', 'GIFT', 'DISCOUNT_CODE']),
                name='chk_after_sales_type_enum'
            ),
            # Protection check: Numerical balance parameters cannot reside inside absolute negative bounds
            models.CheckConstraint(
                check=models.Q(value__gte=0) | models.Q(value__isnull=True),
                name='chk_after_sales_value_positive'
            )
        ]

    def __str__(self):
        """String representation"""
        return f"Tenant {self.tenant_id} - [{self.code}] {self.name} ({self.type})"

    # ========================================================================
    # PRODUCTION SCHEMALESS CONDITION AUDITING & EXTENSION ENGINE
    # ========================================================================

    def clean(self):
        """
        Application-layer structural schema verification validating JSON structural models before DB write locks.
        """
        super().clean()
        
        # Ensure conditions field always initializes as a dictionary structure to protect downstream parser engines
        if not isinstance(self.conditions, dict):
            raise ValidationError({
                'conditions': _('Data Structure Error: The parameters structural rule mapping field must evaluate as a valid JSON object.')
            })
            
        # Core Financial Safety Check: Point injections and Voucher creations require a specific magnitude valuation value
        if self.type in ['VOUCHER', 'LOYALTY_POINTS'] and self.value is None:
            raise ValidationError({
                'value': _('Compliance Exception: Financial rewards like points or monetary vouchers must possess an explicit value parameter.')
            })

    def evaluate_customer_qualification(self, customer_historical_context_dict):
        """
        Processes and filters the schemaless JSONB matrices block against real customer metrics.
        
        Args:
            customer_historical_context_dict: Dict packet representing target client analytics (e.g., {'completed_trips': 3, 'total_spent': 500000})
            
        Returns:
            Boolean status confirming if the reward event should trigger execution blocks.
        """
        if not self.is_active:
            return False
            
        # Dynamic JSON schema extraction and assessment loop
        for key, required_rule_value in self.conditions.items():
            if key in customer_historical_context_dict:
                # Example rule gate: evaluate minimum numeric metrics threshold parameters
                if key.startswith('min_') and customer_historical_context_dict[key] < required_rule_value:
                    return False
                # Example rule gate: evaluate string token configuration matches (e.g. customer tier validation)
                elif key.endswith('_tier') and customer_historical_context_dict[key] != required_rule_value:
                    return False
                    
        return True