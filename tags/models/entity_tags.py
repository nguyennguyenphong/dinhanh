# ============================================================================
# FILE: apps/tags/models.py (Enhanced)
# Entity Tags Models with Audit Trail
# ============================================================================

from django.db import models
from django.db.models import Count, Q
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel


class EntityTag(BaseModel):
    """
    Entity tag model for tagging any entity with audit trail

    Features:
    - Generic tagging: Tag any entity type
    - Audit trail: Track who tagged and when
    - Bulk operations: Batch tag/untag operations
    - Query optimization: Efficient queries with prefetch
    - Tag history: Track tagging changes
    - Composite key: Unique constraint on tag+entity
    - Flexible entity: Support any entity type
    """

    _safedelete_policy = SOFT_DELETE_CASCADE

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    tag = models.ForeignKey(
        "Tag",
        on_delete=models.CASCADE,
        related_name="entity_tags",
        db_index=True,
        help_text="Tag applied to entity",
    )

    # ========================================================================
    # ENTITY LINKING
    # ========================================================================

    entity_type = models.CharField(
        max_length=60,
        db_index=True,
        help_text='Type of entity being tagged (e.g., "bookings", "vehicles")',
    )
    entity_id = models.BigIntegerField(
        db_index=True, help_text="ID of entity being tagged"
    )

    # ========================================================================
    # AUDIT INFORMATION
    # ========================================================================

    tagged_by = models.ForeignKey(
        "accounts.UserAccount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entity_tags_created",
        help_text="User who applied this tag",
    )
    tagged_by_username = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        help_text="Username snapshot at time of tagging",
    )

    # ========================================================================
    # TIMESTAMPS
    # ========================================================================

    tagged_at = models.DateTimeField(
        auto_now_add=True, db_index=True, help_text="When this tag was applied"
    )

    class Meta:
        db_table = "entity_tags"
        verbose_name = _("Entity Tag")
        verbose_name_plural = _("Entity Tags")
        ordering = ["-tagged_at"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            models.UniqueConstraint(
                fields=["tag", "entity_type", "entity_id"],
                name="unique_entity_tag",
                violation_error_message="Entity already has this tag",
            ),
        ]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            models.Index(
                fields=["entity_type", "entity_id"], name="idx_entity_tags_lookup"
            ),
            models.Index(
                fields=["tag", "entity_type"], name="idx_entity_tags_tag_type"
            ),
            models.Index(
                fields=["tagged_by", "tagged_at"], name="idx_entity_tags_user_time"
            ),
        ]

    def __str__(self):
        return f"{self.tag.label} on {self.entity_type}#{self.entity_id}"

    def save(self, *args, **kwargs):
        """Override save to capture username"""
        if self.tagged_by and not self.tagged_by_username:
            self.tagged_by_username = self.tagged_by.username
        super().save(*args, **kwargs)

    # ========================================================================
    # QUERY METHODS - ENTITY TAGS
    # ========================================================================

    @classmethod
    def get_entity_tags(cls, entity_type, entity_id):
        from tags.models.tags import Tag

        return Tag.objects.filter(
            entity_tags__entity_type=entity_type, entity_tags__entity_id=entity_id
        ).distinct()

    @classmethod
    def get_entity_tags_with_info(cls, entity_type, entity_id):
        entity_tags = cls.objects.filter(
            entity_type=entity_type, entity_id=entity_id
        ).select_related("tag", "tagged_by")

        return [
            {
                "tag": et.tag,
                "tagged_by": et.tagged_by_username or "System",
                "tagged_at": et.tagged_at.isoformat(),
                "tagged_by_user": et.tagged_by,
            }
            for et in entity_tags
        ]

    @classmethod
    def has_tag(cls, entity_type, entity_id, tag):
        if isinstance(tag, str):
            return cls.objects.filter(
                entity_type=entity_type, entity_id=entity_id, tag__slug=tag
            ).exists()
        return cls.objects.filter(
            entity_type=entity_type, entity_id=entity_id, tag=tag
        ).exists()

    @classmethod
    def has_any_tag(cls, entity_type, entity_id, tags):
        tag_ids = [t.id for t in tags if not isinstance(t, str)]
        tag_slugs = [t for t in tags if isinstance(t, str)]
        return (
            cls.objects.filter(entity_type=entity_type, entity_id=entity_id)
            .filter(Q(tag_id__in=tag_ids) | Q(tag__slug__in=tag_slugs))
            .exists()
        )

    @classmethod
    def has_all_tags(cls, entity_type, entity_id, tags):
        return cls.objects.filter(
            entity_type=entity_type, entity_id=entity_id
        ).count() == len(tags)

    # ========================================================================
    # QUERY METHODS - TAGGED ENTITIES
    # ========================================================================

    @classmethod
    def get_tagged_entity_ids(cls, tag, entity_type):
        return list(
            cls.objects.filter(tag=tag, entity_type=entity_type).values_list(
                "entity_id", flat=True
            )
        )

    @classmethod
    def get_tagged_entities_count(cls, tag, entity_type):
        return cls.objects.filter(tag=tag, entity_type=entity_type).count()

    @classmethod
    def get_tagged_entities_with_info(cls, tag, entity_type):
        entity_tags = (
            cls.objects.filter(tag=tag, entity_type=entity_type)
            .select_related("tagged_by")
            .order_by("-tagged_at")
        )
        return [
            {
                "entity_id": et.entity_id,
                "tagged_by": et.tagged_by_username or "System",
                "tagged_at": et.tagged_at.isoformat(),
                "tagged_by_user": et.tagged_by,
            }
            for et in entity_tags
        ]

    # ========================================================================
    # QUERY METHODS - COMMON TAGS
    # ========================================================================

    @classmethod
    def get_common_tags(cls, entity_type, entity_ids):
        from tags.models.tags import Tag

        return (
            Tag.objects.filter(
                entity_tags__entity_type=entity_type,
                entity_tags__entity_id__in=entity_ids,
            )
            .annotate(count=Count("id"))
            .filter(count=len(entity_ids))
            .distinct()
        )

    @classmethod
    def get_tags_with_counts(cls, entity_type):
        from tags.models.tags import Tag

        tags = (
            Tag.objects.filter(entity_tags__entity_type=entity_type)
            .annotate(usage_count=Count("entity_tags"))
            .order_by("-usage_count")
        )
        return [(tag, tag.usage_count) for tag in tags]

    # ========================================================================
    # MUTATION METHODS - TAG ENTITY
    # ========================================================================

    @classmethod
    def tag_entity(cls, tag, entity_type, entity_id, tagged_by=None):
        entity_tag, created = cls.objects.get_or_create(
            tag=tag,
            entity_type=entity_type,
            entity_id=entity_id,
            defaults={
                "tagged_by": tagged_by,
                "tagged_by_username": tagged_by.username if tagged_by else None,
            },
        )
        return entity_tag, created

    @classmethod
    def untag_entity(cls, tag, entity_type, entity_id):
        count, _ = cls.objects.filter(
            tag=tag, entity_type=entity_type, entity_id=entity_id
        ).delete()
        return count

    @classmethod
    def bulk_tag_entity(cls, tags, entity_type, entity_id, tagged_by=None):
        return [
            cls.tag_entity(tag, entity_type, entity_id, tagged_by)[0] for tag in tags
        ]

    @classmethod
    def bulk_untag_entity(cls, tags, entity_type, entity_id):
        return sum([cls.untag_entity(tag, entity_type, entity_id) for tag in tags])

    @classmethod
    def clear_entity_tags(cls, entity_type, entity_id):
        count, _ = cls.objects.filter(
            entity_type=entity_type, entity_id=entity_id
        ).delete()
        return count

    @classmethod
    def replace_entity_tags(cls, tags, entity_type, entity_id, tagged_by=None):
        cls.clear_entity_tags(entity_type, entity_id)
        return cls.bulk_tag_entity(tags, entity_type, entity_id, tagged_by)

    # ========================================================================
    # BULK MUTATION METHODS - MULTIPLE ENTITIES
    # ========================================================================

    @classmethod
    def bulk_tag_entities(cls, tag, entity_type, entity_ids, tagged_by=None):
        return [
            cls.tag_entity(tag, entity_type, eid, tagged_by)[0] for eid in entity_ids
        ]

    @classmethod
    def bulk_untag_entities(cls, tag, entity_type, entity_ids):
        count, _ = cls.objects.filter(
            tag=tag, entity_type=entity_type, entity_id__in=entity_ids
        ).delete()
        return count

    # ========================================================================
    # STATISTICS METHODS
    # ========================================================================

    @classmethod
    def get_entity_tag_stats(cls, entity_type, entity_id):
        entity_tags = (
            cls.objects.filter(entity_type=entity_type, entity_id=entity_id)
            .select_related("tag", "tagged_by")
            .order_by("-tagged_at")
        )
        tags_list = [et.tag.slug for et in entity_tags]
        last_tag = entity_tags.first()
        return {
            "total_tags": len(tags_list),
            "tags": tags_list,
            "last_tagged_at": last_tag.tagged_at.isoformat() if last_tag else None,
            "last_tagged_by": last_tag.tagged_by_username if last_tag else None,
        }

    @classmethod
    def get_user_tagging_activity(cls, user, days=30):
        from datetime import timedelta

        from django.utils import timezone

        start_date = timezone.now() - timedelta(days=days)
        entity_tags = cls.objects.filter(tagged_by=user, tagged_at__gte=start_date)
        by_type = {}
        for et in entity_tags:
            by_type[et.entity_type] = by_type.get(et.entity_type, 0) + 1
        return {
            "total_tags": entity_tags.count(),
            "by_entity_type": by_type,
            "period_days": days,
        }
