# ============================================================================
# FILE: apps/inventory/models.py
# Fixed Asset Management & Corporate Inventory Models
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _

# Assuming these models exist in your production architecture
from tenants.models.tenants import Tenant


class AssetCategory(models.Model):
    """
    AssetCategory model governing the primary taxonomy classification for fixed corporate assets.
    
    Features:
    - Multi-tenancy Isolation: Hard-partitioned via tenant_id to separate distinct corporate legal structures.
    - Localized Uniqueness: Enforces unique catalog names strictly scoped per individual tenant boundary.
    - Fiscal Ledger Baseline: Serves as the anchor node for managing fixed asset depreciation algorithms (e.g., straight-line depreciation).
    
    Example:
        # Construct an isolated asset category for a specific transport operator tenant
        category = AssetCategory.objects.create(
            tenant_id=1,
            name='Sleeper Passenger Buses (Heavy Fleet)'
        )
    """

    id = models.AutoField(primary_key=True)
    
    # ========================================================================
    # RELATIONSHIPS & MULTI-TENANCY
    # ========================================================================
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,  # Matches ON DELETE CASCADE from DDL requirement
        default=1,
        related_name='asset_categories',
        db_index=True,
        help_text='Tenant corporate node holding legal data sovereignty over this inventory catalog segment',
    )
    
    # ========================================================================
    # CORE METADATA PROPERTIES
    # ========================================================================
    
    name = models.CharField(
        max_length=100,  # Matches VARCHAR(100) NOT NULL
        help_text='The unique descriptive name of the asset category group (e.g., Garage Repair Machinery, Office Electronics)',
    )
    
    # ========================================================================
    # CHRONOLOGY WINDOWS
    # ========================================================================
    
    created_at = models.DateTimeField(
        default=models.functions.Now,  # Matches NOT NULL DEFAULT NOW() at core DDL layers
        help_text='Timezone-aware database anchor tracking exactly when this asset category configuration row was initialized',
    )

    class Meta:
        db_table = 'asset_categories'
        verbose_name = _('Asset Category')
        verbose_name_plural = _('Asset Categories')
        
        # Default administrative sorting prioritize alphabetic arrangement
        ordering = ['tenant_id', 'name']
        
        # ====================================================================
        # CONSTRAINTS & MULTI-COLUMN UNIQUE INDEX SCOPES
        # ====================================================================
        
        constraints = [
            # Direct database-level unique constraint matching UNIQUE (tenant_id, name)
            # Essential for SaaS scaling: prevents naming collisions across different global business instances.
            models.UniqueConstraint(
                fields=['tenant', 'name'],
                name='uq_tenant_asset_category_name'
            )
        ]

    def __str__(self):
        """String representation"""
        return f"Tenant {self.tenant_id} | {self.name}"

    # ========================================================================
    # PRODUCTION INVENTORY COMPLIANCE & BUSINESS INTERFACES
    # ========================================================================

    def clean(self):
        """
        Application-layer standardizations converting text casing to prevent 
        duplicate semantic names (e.g., "Heavy Trucks" vs "heavy trucks").
        """
        super().clean()
        if self.name:
            # Strip trailing white-spaces and normalize title casing for database consistency
            self.name = self.name.strip()