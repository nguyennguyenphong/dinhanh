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

from tenants.models.tenants import Tenant


class Tag(models.Model):
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
        Tenant,
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

    # ========================================================================
    # TIMESTAMPS
    # ========================================================================

    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, help_text="When this tag was created"
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


class TaggedItem(models.Model):
    """
    Through model for tagging entities
    """

    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name="tagged_items",
        db_index=True,
        help_text="Tag applied to entity",
    )

    # ========================================================================
    # ENTITY LINKING
    # ========================================================================

    entity_type = models.CharField(
        max_length=60, db_index=True, help_text="Type of entity being tagged"
    )
    entity_id = models.IntegerField(
        db_index=True, help_text="ID of entity being tagged"
    )

    # ========================================================================
    # TIMESTAMPS
    # ========================================================================

    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, help_text="When this tag was applied"
    )

    class Meta:
        db_table = "tagged_items"
        verbose_name = _("Tagged Item")
        verbose_name_plural = _("Tagged Items")
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["tag", "entity_type", "entity_id"],
                name="unique_tag_entity",
                violation_error_message="Entity already has this tag",
            ),
        ]

        indexes = [
            models.Index(fields=["entity_type", "entity_id"], name="idx_tagged_entity"),
            models.Index(fields=["tag", "entity_type"], name="idx_tagged_tag_type"),
        ]

    def __str__(self):
        return f"{self.tag.label} on {self.entity_type}#{self.entity_id}"

    # ========================================================================
    # QUERY METHODS
    # ========================================================================

    @classmethod
    def tag_entity(cls, tag, entity_type, entity_id):
        tagged, created = cls.objects.get_or_create(
            tag=tag, entity_type=entity_type, entity_id=entity_id
        )
        return tagged, created

    @classmethod
    def untag_entity(cls, tag, entity_type, entity_id):
        count, _ = cls.objects.filter(
            tag=tag, entity_type=entity_type, entity_id=entity_id
        ).delete()
        return count

    @classmethod
    def get_entity_tags(cls, entity_type, entity_id):
        return Tag.objects.filter(
            tagged_items__entity_type=entity_type, tagged_items__entity_id=entity_id
        ).distinct()

    @classmethod
    def get_tagged_items(cls, tag, entity_type=None):
        query = cls.objects.filter(tag=tag)
        if entity_type:
            query = query.filter(entity_type=entity_type)
        return query.order_by("-created_at")

    @classmethod
    def get_entity_ids_with_tag(cls, tag, entity_type):
        return list(
            cls.objects.filter(tag=tag, entity_type=entity_type).values_list(
                "entity_id", flat=True
            )
        )

    @classmethod
    def bulk_tag(cls, tags, entity_type, entity_id):
        return [cls.tag_entity(tag, entity_type, entity_id)[0] for tag in tags]

    @classmethod
    def bulk_untag(cls, tags, entity_type, entity_id):
        return sum([cls.untag_entity(tag, entity_type, entity_id) for tag in tags])

    @classmethod
    def clear_entity_tags(cls, entity_type, entity_id):
        count, _ = cls.objects.filter(
            entity_type=entity_type, entity_id=entity_id
        ).delete()
        return count

    @classmethod
    def get_common_tags(cls, entity_type, entity_ids):
        from django.db.models import Count

        return (
            Tag.objects.filter(
                tagged_items__entity_type=entity_type,
                tagged_items__entity_id__in=entity_ids,
            )
            .annotate(count=Count("id"))
            .filter(count=len(entity_ids))
            .distinct()
        )

    @classmethod
    def get_tags_with_counts(cls, tenant, entity_type=None):
        from django.db.models import Count

        query = (
            Tag.objects.filter(tenant=tenant)
            .annotate(usage_count=Count("tagged_items"))
            .order_by("-usage_count")
        )
        if entity_type:
            query = query.filter(tagged_items__entity_type=entity_type).distinct()
        return [(tag, tag.usage_count) for tag in query]
