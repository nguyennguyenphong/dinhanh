# ============================================================================
# FILE: apps/finance/models.py
# Corporate Finance, Budgeting & Expense Category Models
# ============================================================================

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class ExpenseCategory(BaseModel):
    """
    ExpenseCategory model deploying a self-referential tree structure to classify corporate outlays.

    Features:
    - Multi-tenancy Isolation: Hard-partitioned via tenant_id with localized unique code scopes.
    - Adjacency List Hierarchy: Employs a self-linking pointer (parent_id) to map nested cost centers.
    - Anti-Loop Validation: Includes application-layer checks blocking nodes from linking into themselves.

    Hierarchical Mapping Example:
        - OPERATIONAL_EXPENSES (Root Node)
            ├── FUEL_COSTS (Child Node linking back to parent_id=OPERATIONAL_EXPENSES)
            └── TOLL_FEES (Child Node linking back to parent_id=OPERATIONAL_EXPENSES)

    Example:
        # Construct an active root-level corporate expense ledger node
        root_category = ExpenseCategory.objects.create(
            tenant_id=1,
            code='FLEET_MAINTENANCE',
            name='Fleet Garage & Repair Expenditures'
        )

        # Link a sub-category directly under the parent node
        sub_category = ExpenseCategory.objects.create(
            tenant_id=1,
            code='TIRE_REPLACEMENT',
            name='Heavy Truck Tire Rotation & Purchase Logistics',
            parent=root_category
        )
    """

    id = models.AutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS & MULTI-TENANCY
    # ========================================================================

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,  # Matches ON DELETE CASCADE from requirement
        default=1,
        related_name="expense_categories",
        db_index=True,
        help_text="Tenant corporate corporate node holding legal data sovereignty over this account code structure",
    )

    # ========================================================================
    # SELF-REFERENTIAL HIERARCHICAL TREE LINK (ADJACENCY LIST)
    # ========================================================================

    parent = models.ForeignKey(
        "self",  # Employs a recursive self-referential linkage relationship
        on_delete=models.SET_NULL,  # Matches REFERENCES expense_categories(id) ON DELETE SET NULL
        related_name="subcategories",
        null=True,
        blank=True,
        db_index=True,
        help_text="Pointer referencing the higher-level master accounting classification group. Sits NULL for root categories.",
    )

    # ========================================================================
    # CORE IDENTITY METADATA
    # ========================================================================

    code = models.CharField(
        max_length=30,  # Matches VARCHAR(30) NOT NULL
        help_text="The specialized uppercase system billing key token (e.g., FUEL_DIESEL, OFFICE_RENT)",
    )

    name = models.CharField(
        max_length=100,  # Matches VARCHAR(100) NOT NULL
        help_text="Human-readable balance sheet title label used across corporate ledger accounting dashboards",
    )

    class Meta:
        db_table = "expense_categories"
        verbose_name = _("Corporate Expense Category")
        verbose_name_plural = _("Corporate Expense Categories")

        # Enforces default ordering to compile hierarchical trees elegantly inside select selections
        ordering = ["tenant", "parent_id", "code"]

        # ====================================================================
        # CONSTRAINTS & MULTI-COLUMN UNIQUE INDEX SCOPES
        # ====================================================================

        constraints = [
            # Replicates exact structure of UNIQUE (tenant_id, code)
            models.UniqueConstraint(
                fields=["tenant", "code"], name="uq_tenant_expense_category_code"
            )
        ]

    def __str__(self):
        """String representation showing structural inheritance hierarchy"""
        if self.parent_id:
            return f"Tenant {self.tenant_id} | {self.parent.code} -> {self.code} ({self.name})"
        return f"Tenant {self.tenant_id} | [{self.code}] {self.name} (Root)"

    # ========================================================================
    # ARCHITECTURAL TREE INTEGRITY GUARD RAILS
    # ========================================================================

    def clean(self):
        """
        Application-layer structural integrity check preventing infinite recursive loops inside accounting records.
        """
        super().clean()

        if self.id and self.parent_id:
            # 1. Verification Gate: Prevent a node from setting itself as its own parent (Self-Loop Deflection)
            if self.id == self.parent_id:
                raise ValidationError(
                    {
                        "parent": _(
                            "Hierarchical Integrity Error: A financial expense category cannot mathematically assign itself as its own parent group."
                        )
                    }
                )

            # 2. Multi-Tenancy Cross Leak Check: Ensure child nodes belong to the exact same tenant group as their parent node
            if self.tenant_id != self.parent.tenant_id:
                raise ValidationError(
                    {
                        "parent": _(
                            "Cross-Tenant Data Leak Error: Target parent classification group resides inside a different tenant data silo boundary."
                        )
                    }
                )

            # 3. Prevent Deep Nesting Vulnerabilities (Production Best Practice: Hard-cap hierarchy at 3 levels)
            # This protects reporting systems from stack overflow loops during tree traversal.
            current_parent = self.parent
            nesting_depth = 1
            while current_parent is not None:
                nesting_depth += 1
                if nesting_depth > 3:
                    raise ValidationError(
                        {
                            "parent": _(
                                "Operational Limit Error: System restrictions enforce a maximum architectural depth of 3 nested catalog layers."
                            )
                        }
                    )
                current_parent = current_parent.parent

    def get_all_children_ids(self):
        """
        Recursive lookup engine gathering all downstream node identities nested under this category.
        Highly optimized for clearing bulk expense rows linked to entire groups.

        Returns:
            List of primary key integers matching subcategories.
        """
        children_ids = []
        # Uses Django prefetch/select caches dynamically if pulled into memory properly
        for child in self.subcategories.all():
            children_ids.append(child.id)
            children_ids.extend(child.get_all_children_ids())
        return children_ids
