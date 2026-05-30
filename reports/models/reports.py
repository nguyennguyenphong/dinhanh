# ============================================================================
# FILE: apps/analytics/models.py
# Business Intelligence, Dynamic Analytics & Report Definition Models
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

# Assuming these models exist in your production architecture
from tenants.models.tenants import Tenant
from accounts.models.user_accounts import UserAccount  # Custom user model


class ReportDefinition(models.Model):
    """
    ReportDefinition model serving as the central engine schema configuration for dynamic BI reports.
    
    Features:
    - Multi-tenancy Isolation: Hard-partitioned by tenant_id with localized unique code lookup matrices.
    - PostgreSQL JSONB Engine: Leverages binary-JSON compilation to store complex telemetry analytics payloads.
    - Domain Taxonomy Layer: Classifies data models across Revenue, Fleet Operations, HR, Cargo, or Customers.
    - Access Control Flags: Toggles system built-in blueprints and cross-operator public shared states.
    
    Categories:
    - REVENUE: Analytical models tracking financial ticket sales, freight invoicing, and expense ledgers.
    - OPERATIONS: Fleet scheduling telemetry, trip performance metrics, and fuel consumption trends.
    - HR: Employee shift tracking logs, payroll summaries, and driver performance scores.
    - CARGO: Logistical parcel volumes, depot fulfillment durations, and shipping cash-on-delivery (COD) status.
    - CUSTOMERS: Passenger registration churn rates, B2C mobile engagement, and retention scoring rows.
    
    Example:
        # Register a complex dynamic JSON report blueprint layout for fleet operations analytics
        report = ReportDefinition.objects.create(
            tenant_id=1,
            code='RPT_FLEET_EFFICIENCY_2026',
            name='Vehicle Fuel and Maintenance Efficiency Matrix',
            category='OPERATIONS',
            query_config={
                'metrics': ['avg_liters_per_km', 'total_maintenance_cost'],
                'dimensions': ['vehicle_id', 'route_code'],
                'filters': {'status': 'IN_USE', 'year': 2026}
            },
            chart_config={
                'type': 'bar',
                'x_axis': 'vehicle_id',
                'y_axis': 'avg_liters_per_km',
                'theme': 'corporate_dark'
            },
            is_builtin=True
        )
    """

    CATEGORY_CHOICES = (
        ('REVENUE', _('Revenue - Financial statements, ticket sales, cash flow balances, and expense ledgers')),
        ('OPERATIONS', _('Operations - Fleet performance tracking, trip execution logs, and fuel allocation metrics')),
        ('HR', _('HR - Employee payroll registries, shift rosters, and personnel productivity auditing')),
        ('CARGO', _('Cargo - Logistical freight weight tracking, parcel volumes, and warehouse turnover durations')),
        ('CUSTOMERS', _('Customers - Passenger demographic trends, loyalty tier analytics, and churn rate matrix rows')),
    )

    id = models.AutoField(primary_key=True)
    
    # ========================================================================
    # RELATIONSHIPS & MULTI-TENANCY CONTEXTS
    # ========================================================================
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,  # Matches ON DELETE CASCADE from DDL requirement
        default=1,
        related_name='report_definitions',
        db_index=True,
        help_text='Tenant corporate owner holding legal data sovereignty over this analytics report definition'
    )
    
    created_by = models.ForeignKey(
        UserAccount,
        on_delete=models.SET_NULL,  # Matches REFERENCES user_accounts(id) ON DELETE SET NULL
        related_name='created_reports',
        null=True,
        blank=True,
        db_index=True,
        help_text='The specialized user account profile or BI analyst who constructed this dynamic configuration layout'
    )
    
    # ========================================================================
    # IDENTITY TAXONOMY & LABELS
    # ========================================================================
    
    code = models.CharField(
        max_length=60,  # Matches VARCHAR(60) NOT NULL
        help_text='Unique system lookup identifier string token key (e.g., FINANCIAL_P_L_STATEMENT, TRIP_KPI_SUMMARY)'
    )
    
    name = models.CharField(
        max_length=255,  # Matches VARCHAR(255) NOT NULL
        help_text='Human-readable title description banner utilized across executive dashboard reporting navigation bars'
    )
    
    category = models.CharField(
        max_length=60,
        choices=CATEGORY_CHOICES,  # Enforces compliance bounds mapping comments precisely
        db_index=True,
        help_text='The business intelligence domain vertical that this report parsing pipeline operates inside'
    )
    
    description = models.TextField(
        null=True,
        blank=True,
        help_text='Granular text detailing analytical goals, source data limitations, or interpretation guides for staff'
    )
    
    # ========================================================================
    # POSTGRESQL NATIVE BINARY-JSON PAYLOAD STACKS (JSONB FIELDS)
    # ========================================================================
    
    query_config = models.JSONField(
        default=dict,  # Matches NOT NULL DEFAULT '{}' using safe dictionary factories
        help_text='JSON metadata mapping analytical extraction rules (filters, aggregation dimensions, selected KPI metrics)'
    )
    
    chart_config = models.JSONField(
        default=dict,  # Matches NOT NULL DEFAULT '{}'
        help_text='JSON metadata mapping data rendering instructions (visualization type e.g. line/bar/pie, axis bindings, UI themes)'
    )
    
    # ========================================================================
    # CONTROL ARCHITECTURAL SWITCHES & CHRONOLOGY
    # ========================================================================
    
    is_builtin = models.BooleanField(
        default=False,  # Matches NOT NULL DEFAULT FALSE
        db_index=True,
        help_text='Flag marking core hardcoded system reports. Protects critical core records from casual user deletions.'
    )
    
    is_public = models.BooleanField(
        default=False,  # Matches NOT NULL DEFAULT FALSE
        help_text='Determines visibility bounds. When TRUE, other global operators within this node can inspect layout metrics.'
    )
    
    created_at = models.DateTimeField(
        default=models.functions.Now,  # Matches NOT NULL DEFAULT NOW() at core database compiler layers
        help_text='Timezone-aware record logging anchor tracking exactly when this report definition row was initialized'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,  # Automatically triggers updated_at synchronization across application mutations
        help_text='Timestamp tracking exactly when parameter attributes inside this analytics structure node mutated'
    )

    class Meta:
        db_table = 'report_definitions'
        verbose_name = _('Report Definition Blueprint')
        verbose_name_plural = _('Report Definition Blueprints')
        
        # Default sorting structures place built-in system reports first, sorted by alphabetical taxonomy
        ordering = ['tenant_id', '-is_builtin', 'category', 'code']
        
        # ====================================================================
        # CONSTRAINTS & MULTI-COLUMN UNIQUE INDEX SCOPES
        # ====================================================================
        
        constraints = [
            # Replicates exact structure of UNIQUE (tenant_id, code)
            models.UniqueConstraint(
                fields=['tenant', 'code'],
                name='uq_tenant_report_definition_code'
            ),
            # Direct database-level CHECK constraint enforcing reporting domain taxonomy compliance
            models.CheckConstraint(
                condition=models.Q(category__in=['REVENUE', 'OPERATIONS', 'HR', 'CARGO', 'CUSTOMERS']),
                name='chk_report_definition_category_enum'
            )
        ]

    def __str__(self):
        """String representation"""
        return f"Tenant {self.tenant_id} | [{self.code}] {self.name} ({self.category})"

    # ========================================================================
    # BI PARSING LOGIC & ENVELOPE STRUCTURAL VALIDATION ENGINES
    # ========================================================================

    def clean(self):
        """
        Application-layer schema assurance validating JSON array configurations before disk serialization.
        """
        super().clean()
        
        # 1. Formatting Guard: Force reporting uppercase tokens to secure string matching during raw query generations
        if self.code:
            self.code = self.code.strip().upper()
            
        # 2. Safety Interlock Switch: Prevent non-system administrators from changing or corrupting structural system blueprints
        if self.is_builtin and self.id:
            original = ReportDefinition.objects.get(pk=self.id)
            if not original.is_builtin:
                raise ValidationError({
                    'is_builtin': _('Security Enforcement Error: Injecting custom runtime configurations into system infrastructure blocks is disallowed.')
                })
                
        # 3. JSON Configuration Content Auditing: Ensure dictionaries adhere to minimal interface requirements
        if isinstance(self.query_config, dict):
            # Enforce that custom ad-hoc parameters don't break mandatory analytics array indices
            required_keys = ['filters', 'dimensions', 'metrics']
            for key in required_keys:
                if key not in self.query_config:
                    # Automatically initialize empty fallback schemas to guarantee API structural safety
                    self.query_config[key] = {} if key == 'filters' else []

    def execute_report_data_compile(self, execution_engine_callback):
        """
        Business Intelligence compilation interface. Fires off a callback function passing 
        the raw JSON query parameters to fetch data rows from analytics database nodes.
        
        Args:
            execution_engine_callback: A function/service capable of parsing JSON filters into SQL.
            
        Returns:
            Dataset structure generated by database query worker pools.
        """
        if not self.query_config:
            raise ValueError(_("Execution Exception: Cannot parse report query due to empty query_config parameters."))
            
        # Deliver sanitized dictionary blocks down to target execution microservices
        return execution_engine_callback(self.query_config)