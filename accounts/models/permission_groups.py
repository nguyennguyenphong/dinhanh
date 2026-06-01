from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

class PermissionGroup(models.Model):
    """
    Group related permissions together for easier management

    Features:
    - Organize permissions by functional groups
    - Assign multiple permissions at once
    - Simplify role creation

    Example:
        PermissionGroup.objects.create(
            tenant=tenant,
            code='tickets_full_access',
            name='Full Ticket Access',
            description='All permissions for ticket management'
        )
    """

    id = models.AutoField(primary_key=True)

    # Multi-tenant relationship
    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="permission_groups",
        db_index=True,
        help_text="Tenant that owns this permission group",
    )

    # Group identification
    code = models.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                regex=r"^[a-z0-9_]+$",
                message="Code must contain only lowercase letters, numbers, and underscores",
            )
        ],
        help_text='Unique group code (e.g., "tickets_full_access")',
    )
    name = models.CharField(
        max_length=255, help_text="Display name for permission group"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of what permissions this group includes",
    )

    # Permissions in this group
    permissions = models.ManyToManyField(
        "accounts.Permission",
        related_name="groups",
        help_text="Permissions included in this group",
    )

    # Status
    is_active = models.BooleanField(
        default=True, db_index=True, help_text="Inactive groups cannot be assigned"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "permission_groups"
        verbose_name = _("Permission Group")
        verbose_name_plural = _("Permission Groups")
        ordering = ["name"]

        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "code"], name="unique_tenant_permission_group_code"
            ),
        ]

        indexes = [
            models.Index(fields=["tenant", "is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.tenant.code})"

    def get_permission_codes(self):
        """
        Get list of all permission codes in this group

        Returns:
            List of permission codenames
        """
        return list(
            self.permissions.filter(is_active=True).values_list("codename", flat=True)
        )