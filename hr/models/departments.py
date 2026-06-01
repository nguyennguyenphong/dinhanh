# ============================================================================
# FILE: apps/departments/models.py
# Departments Management Models
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _


class Department(models.Model):
    """
    Department model for organizing corporate structure and staff segmentation per tenant.

    Features:
    - Multi-tenancy: Isolated and partitioned securely via tenant_id
    - Unique Constraint: Department name must be unique within a single tenant scope
    - Leadership Mapping: Relates to a UserAccount acting as the department manager
    - Operational Indexing: Optimized for high-speed tenant structure directory queries

    Example:
        # Create a new department
        dept = Department.objects.create(
            tenant_id=1,
            name='Logistics Operations',
            manager=manager_user_instance
        )
    """

    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS & MULTI-TENANCY
    # ========================================================================

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        default=1,
        related_name="departments",
        db_index=True,
        help_text="Tenant owner of this department corporate division",
    )

    manager = models.ForeignKey(
        "accounts.UserAccount",
        on_delete=models.SET_NULL,  # Matches ON DELETE SET NULL from requirement
        related_name="managed_departments",
        null=True,
        blank=True,
        db_index=True,
        help_text="The staff account designated as the head/manager of this division",
    )

    # ========================================================================
    # DEPARTMENT CORE INFORMATION
    # ========================================================================

    name = models.CharField(
        max_length=100,
        help_text="Official name of the department (e.g., Human Resources, Accounting)",
    )

    # ========================================================================
    # TIMESTAMPS
    # ========================================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Timestamp when this corporate department was registered",
    )

    class Meta:
        db_table = "departments"
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")
        ordering = ["tenant", "name"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Ensures name uniqueness within a single tenant scope (Matches UNIQUE (tenant_id, name))
            models.UniqueConstraint(
                fields=["tenant", "name"], name="unique_tenant_department_name"
            ),
        ]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Composite index optimizing organizational charts and staff filters by department names
            models.Index(
                fields=["tenant", "name"],
                name="idx_dept_tenant_name_lookup",
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.name} (Tenant #{self.tenant_id})"

    # ========================================================================
    # BUSINESS LOGIC & ORG METHODS
    # ========================================================================

    def has_manager(self):
        """
        Check if the department currently has an assigned active manager.

        Returns:
            Boolean
        """
        return self.manager is not None

    def assign_new_manager(self, user_instance):
        """
        Safely update the leadership manager head for this division.

        Args:
            user_instance: UserAccount model instance
        """
        self.manager = user_instance
        self.save(update_fields=["manager"])

    # ========================================================================
    # CLASSMETHODS / CORE MANAGEMENT QUERY LOGIC
    # ========================================================================

    @classmethod
    def get_departments_by_tenant(cls, tenant_id):
        """
        Fetch all active corporate divisions mapped beneath a shared business tenant.

        Args:
            tenant_id: Integer

        Returns:
            QuerySet of Department objects with optimized pre-fetched manager accounts
        """
        return (
            cls.objects.filter(tenant_id=tenant_id)
            .select_related("manager")
            .order_by("name")
        )
