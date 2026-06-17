# ============================================================================
# FILE: apps/tags/models.py
# Tag Models with Flexible Tagging Support
# ============================================================================

import re

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class Tag(BaseModel):
    """
    Tag model for categorizing and organizing content

    Features:
    - Multi-tenant support: Each tenant has own tags
    - Slug-based: URL-friendly identifiers
    - Color coding: Visual identification with hex colors
    - Reusable: Tags can be applied to multiple entities
    - Bulk operations: Batch tag/untag operations
    - Query support: Filter by tags
    - Auto-slugify: Automatic slug generation
    """

    id = models.AutoField(primary_key=True)

    # ========================================================================
    # MULTI-TENANT RELATIONSHIP
    # ========================================================================

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="tags",
        db_index=True,
        help_text="Tenant that owns this tag",
    )

    # ========================================================================
    # TAG IDENTIFICATION
    # ========================================================================

    slug = models.CharField(
        max_length=80,
        validators=[
            RegexValidator(
                regex=r"^[a-z0-9\-]+$",
                message="Slug must contain only lowercase letters, numbers, and hyphens",
            )
        ],
        help_text='URL-friendly identifier (e.g., "vip-customer")',
    )
    label = models.CharField(
        max_length=100, help_text='Human-readable label (e.g., "VIP Customer")'
    )

    # ========================================================================
    # DISPLAY
    # ========================================================================

    color = models.CharField(
        max_length=7,
        default="#6B7280",
        validators=[
            RegexValidator(
                regex=r"^#[0-9A-Fa-f]{6}$",
                message="Color must be a valid hex color (e.g., #6B7280)",
            )
        ],
        help_text="Hex color code for visual identification",
    )

    class Meta:
        db_table = "tags"
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ["label"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "slug"],
                name="unique_tenant_tag_slug",
                violation_error_message="Tag slug must be unique within tenant",
            ),
        ]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            models.Index(fields=["tenant"], name="idx_tag_tenant"),
            models.Index(fields=["slug"], name="idx_tag_slug"),
        ]

    def __str__(self):
        return f"{self.label} ({self.tenant.code})"

    def clean(self):
        if not self.slug:
            self.slug = slugify(self.label)
        if not re.match(r"^[a-z0-9\-]+$", self.slug):
            raise ValidationError(
                "Slug must contain only lowercase letters, numbers, and hyphens"
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    # ========================================================================
    # QUERY METHODS
    # ========================================================================

    @classmethod
    def get_tag(cls, tenant, slug):
        try:
            return cls.objects.get(tenant=tenant, slug=slug)
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_or_create_tag(cls, tenant, label, slug=None, color="#6B7280"):
        if not slug:
            slug = slugify(label)
        tag, created = cls.objects.get_or_create(
            tenant=tenant, slug=slug, defaults={"label": label, "color": color}
        )
        return tag, created

    @classmethod
    def get_all_tags(cls, tenant):
        return cls.objects.filter(tenant=tenant).order_by("label")

    @classmethod
    def search_tags(cls, tenant, query):
        from django.db.models import Q

        return (
            cls.objects.filter(tenant=tenant)
            .filter(Q(label__icontains=query) | Q(slug__icontains=query))
            .order_by("label")
        )
