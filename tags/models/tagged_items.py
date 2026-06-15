from django.db import models
from django.utils.translation import gettext_lazy as _
from safedelete.models import SOFT_DELETE_CASCADE, SafeDeleteModel


class TaggedItem(SafeDeleteModel):
    """
    Through model for tagging entities
    """

    _safedelete_policy = SOFT_DELETE_CASCADE

    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    tag = models.ForeignKey(
        "tags.Tag",
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
        from django.apps import apps

        Tag = apps.get_model("tags", "Tag")
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
        from django.apps import apps
        from django.db.models import Count

        Tag = apps.get_model("tags", "Tag")
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
        from django.apps import apps
        from django.db.models import Count

        Tag = apps.get_model("tags", "Tag")
        query = (
            Tag.objects.filter(tenant=tenant)
            .annotate(usage_count=Count("tagged_items"))
            .order_by("-usage_count")
        )
        if entity_type:
            query = query.filter(tagged_items__entity_type=entity_type).distinct()
        return [(tag, tag.usage_count) for tag in query]
