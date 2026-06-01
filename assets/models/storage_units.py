# ============================================================================
# FILE: apps/inventory/models.py
# Inventory Logistics & Physical Storage Unit Models
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

# Assuming these models exist in your production architecture
from tenants.models.tenants import Tenant
from branches.models.branches import Branch


class StorageUnit(models.Model):
    """
    StorageUnit model representing a physical inventory warehouse, depot, or stockroom location.

    Features:
    - Multi-tenancy Isolation: Partitioned by tenant_id to isolate inventory across distinct corporate entities.
    - Branch-Aware Mapping: Anchors storage facilities directly onto organizational geographic nodes/offices.
    - Localized Alphanumeric Tagging: Enforces unique tracking codes per tenant block to prevent naming conflicts.

    Example:
        # Register an active localized parcel warehouse bound to a specific regional branch office
        depot = StorageUnit.objects.create(
            tenant_id=1,
            code='WH_HCM_EAST_01',
            name='Mien Dong Bus Station Main Goods Storage Depot',
            branch_id=5,
            description='Primary multi-tier parcel shelf facility dedicated to outbound logistics cargo.'
        )
    """

    id = models.AutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS & MULTI-TENANCY CONTEXTS
    # ========================================================================

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,  # Matches ON DELETE CASCADE from DDL requirement
        default=1,
        related_name="storage_units",
        db_index=True,
        help_text="Tenant corporate node holding legal data sovereignty over this inventory location cluster",
    )

    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,  # Matches REFERENCES branches(id) ON DELETE SET NULL
        related_name="storage_units",
        null=True,
        blank=True,
        db_index=True,
        help_text="The specific regional corporate branch office or shipping station controlling this physical depot",
    )

    # ========================================================================
    # CORE IDENTITY METADATA
    # ========================================================================

    code = models.CharField(
        max_length=30,  # Matches VARCHAR(30) NOT NULL
        help_text="Unique system identifier text key assigned to this warehouse facility (e.g., KHO_LOGISTICS_Q5)",
    )

    name = models.CharField(
        max_length=100,  # Matches VARCHAR(100) NOT NULL
        help_text="Human-readable descriptive title label identifying this physical stockroom location",
    )

    description = models.TextField(
        null=True,
        blank=True,
        help_text="Granular physical details, operation hours, capacity restrictions, or logistical notes",
    )

    # ========================================================================
    # CONTROL CHRONOLOGY WINDOWS
    # ========================================================================

    created_at = models.DateTimeField(
        default=models.functions.Now,  # Matches NOT NULL DEFAULT NOW() at core database compiler layers
        help_text="Timezone-aware log record tracking exactly when this storage site was added to the platform",
    )

    updated_at = models.DateTimeField(
        auto_now=True,  # Automatically syncs database row mutation operations via application hooks
        help_text="Timestamp tracking exactly when parameter attributes inside this storage configuration node changed",
    )

    class Meta:
        db_table = "storage_units"
        verbose_name = _("Inventory Storage Unit")
        verbose_name_plural = _("Inventory Storage Units")

        # Enforces systematic ordering to sort depots by tenant and code hierarchies inside admin select tools
        ordering = ["tenant_id", "code"]

        # ====================================================================
        # CONSTRAINTS & MULTI-COLUMN UNIQUE INDEX SCOPES
        # ====================================================================

        constraints = [
            # Direct database-level unique constraint matching UNIQUE (tenant_id, code)
            # Essential for SaaS scaling: prevents code naming collisions across different global tenants.
            models.UniqueConstraint(
                fields=["tenant", "code"], name="uq_tenant_storage_unit_code"
            )
        ]

    def __str__(self):
        """String representation"""
        return f"Tenant {self.tenant_id} | [{self.code}] {self.name}"

    # ========================================================================
    # PRODUCTION LOGISTICS COMPLIANCE & CROSS-LEAK FILTERS
    # ========================================================================

    def clean(self):
        """
        Application-layer structural validation auditing cross-tenant system invariants.
        """
        super().clean()

        # 1. Formatting Guard: Normalize lookup code tokens to clean string layouts before committing to disk
        if self.code:
            self.code = self.code.strip().upper()

        # 2. Multi-Tenant Cross-Leak Shield: Validate parent organizational context matching tenant boundaries
        if self.branch_id and self.tenant_id != self.branch.tenant_id:
            raise ValidationError(
                {
                    "branch": _(
                        "Cross-Tenant Data Leak Error: Target corporate branch assigned to this storage unit belongs to a different tenant."
                    )
                }
            )
