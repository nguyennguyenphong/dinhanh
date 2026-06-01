# ============================================================================
# FILE: apps/accounts/models.py
# Roles, Permissions, and User Account Models
# ============================================================================

import uuid

from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.core.validators import RegexValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from tenants.models.tenants import Tenant


class Role(models.Model):
    """
    Role model for multi-tenant RBAC (Role-Based Access Control)

    Features:
    - Multi-tenant support: Each tenant has their own roles
    - System roles: Built-in roles that cannot be deleted
    - Slug-based identification: Unique identifier for each role
    - Soft delete support: Can be deactivated instead of deleted

    Example:
        Role.objects.create(
            tenant_id=1,
            name="Super Administrator",
            slug="super-admin",
            description="Full system access",
            is_system=True
        )
    """

    id = models.AutoField(primary_key=True)

    # Multi-tenant relationship
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="roles",
        db_index=True,
        help_text="Tenant that owns this role",
    )

    # Role identification
    name = models.CharField(
        max_length=100,
        help_text='Display name of the role (e.g., "Super Administrator")',
    )
    slug = models.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                regex=r"^[a-z0-9-]+$",
                message="Slug must contain only lowercase letters, numbers, and hyphens",
            )
        ],
        help_text='Unique identifier for the role (e.g., "super-admin", "cashier")',
    )
    description = models.TextField(
        blank=True, null=True, help_text="Detailed description of role responsibilities"
    )

    # System flags
    is_system = models.BooleanField(
        default=False,
        help_text="System roles cannot be deleted and have predefined permissions",
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Inactive roles cannot be assigned to users",
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "roles"
        verbose_name = _("Role")
        verbose_name_plural = _("Roles")
        ordering = ["name"]

        # Unique constraint: slug must be unique per tenant
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "slug"], name="unique_tenant_role_slug"
            ),
        ]

        # Indexes for common queries
        indexes = [
            models.Index(fields=["tenant", "is_active"]),
            models.Index(fields=["is_system"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.tenant.code})"

    def save(self, *args, **kwargs):
        """
        Override save to auto-generate slug if not provided
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def can_be_deleted(self):
        """
        Check if role can be deleted
        System roles and roles with users cannot be deleted
        """
        if self.is_system:
            return False
        return not self.users.exists()

    def get_permissions(self):
        """
        Get all permissions assigned to this role
        Returns: QuerySet of Permission objects
        """
        return self.permissions.filter(is_active=True)

    def get_permission_codes(self):
        """
        Get list of permission codes for this role
        Useful for checking permissions in views
        Returns: List of permission codes (e.g., ['tickets.view', 'tickets.create'])
        """
        return list(
            self.permissions.filter(is_active=True).values_list("code", flat=True)
        )
