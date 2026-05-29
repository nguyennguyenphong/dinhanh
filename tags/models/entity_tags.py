# ============================================================================
# FILE: apps/tags/models.py (Enhanced)
# Entity Tags Models with Audit Trail
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count


class EntityTag(models.Model):
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
    
    Entity Types:
    - vehicles: Vehicle records
    - bookings: Booking records
    - employees: Employee records
    - trips: Trip records
    - invoices: Invoice records
    - receipts: Receipt records
    - documents: Document records
    - custom: Custom entity types
    
    Use Cases:
    - Tag vehicles as 'premium', 'economy', 'maintenance'
    - Tag bookings as 'vip', 'urgent', 'completed'
    - Tag employees as 'driver', 'mechanic', 'manager'
    - Tag trips as 'express', 'standard', 'charter'
    - Tag documents as 'important', 'archived', 'draft'
    
    Example:
        # Tag entity
        entity_tag = EntityTag.objects.create(
            tag=tag,
            entity_type='bookings',
            entity_id=booking.id,
            tagged_by=user
        )
        
        # Get entity tags
        tags = EntityTag.get_entity_tags('bookings', booking.id)
        
        # Get tagged entities
        entity_ids = EntityTag.get_tagged_entity_ids(tag, 'bookings')
        
        # Bulk tag
        EntityTag.bulk_tag_entity(tags, 'bookings', booking.id, user)
    """

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================
    
    tag = models.ForeignKey(
        'Tag',
        on_delete=models.CASCADE,
        related_name='entity_tags',
        db_index=True,
        help_text='Tag applied to entity',
        db_comment='Reference to tag'
    )
    
    # ========================================================================
    # ENTITY LINKING
    # ========================================================================
    
    entity_type = models.CharField(
        max_length=60,
        db_index=True,
        help_text='Type of entity being tagged (e.g., "bookings", "vehicles")',
        db_comment='Entity type'
    )
    entity_id = models.BigIntegerField(
        db_index=True,
        help_text='ID of entity being tagged',
        db_comment='Entity ID'
    )
    
    # ========================================================================
    # AUDIT INFORMATION
    # ========================================================================
    
    tagged_by = models.ForeignKey(
        'accounts.UserAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='entity_tags_created',
        help_text='User who applied this tag',
        db_comment='Tagged by user'
    )
    tagged_by_username = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        help_text='Username snapshot at time of tagging',
        db_comment='Username snapshot'
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    tagged_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='When this tag was applied',
        db_comment='Tagging timestamp'
    )

    class Meta:
        db_table = 'entity_tags'
        verbose_name = _('Entity Tag')
        verbose_name_plural = _('Entity Tags')
        ordering = ['-tagged_at']
        
        # ====================================================================
        # CONSTRAINTS
        # ====================================================================
        
        constraints = [
            # Composite primary key: tag + entity_type + entity_id
            models.UniqueConstraint(
                fields=['tag', 'entity_type', 'entity_id'],
                name='unique_entity_tag',
                violation_error_message='Entity already has this tag'
            ),
        ]
        
        # ====================================================================
        # INDEXES
        # ====================================================================
        
        indexes = [
            # Index for finding tags on entity
            models.Index(
                fields=['entity_type', 'entity_id'],
                name='idx_entity_tags_lookup',
                db_comment='Query tags by entity'
            ),
            # Index for finding entities with tag
            models.Index(
                fields=['tag', 'entity_type'],
                name='idx_entity_tags_tag_type',
                db_comment='Query entities by tag and type'
            ),
            # Index for audit queries
            models.Index(
                fields=['tagged_by', 'tagged_at'],
                name='idx_entity_tags_user_time',
                db_comment='Query tags by user and time'
            ),
        ]

    def __str__(self):
        """String representation"""
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
        """
        Get all tags for an entity
        
        Args:
            entity_type: Entity type
            entity_id: Entity ID
        
        Returns:
            QuerySet of Tag objects
        
        Example:
            tags = EntityTag.get_entity_tags('bookings', booking.id)
        """
        from tags.models.tags import Tag
        
        return Tag.objects.filter(
            entity_tags__entity_type=entity_type,
            entity_tags__entity_id=entity_id
        ).distinct()

    @classmethod
    def get_entity_tags_with_info(cls, entity_type, entity_id):
        """
        Get tags with tagging info for an entity
        
        Args:
            entity_type: Entity type
            entity_id: Entity ID
        
        Returns:
            List of dicts with tag and tagging info
        
        Example:
            tags_info = EntityTag.get_entity_tags_with_info('bookings', booking.id)
            # Returns: [
            #     {
            #         'tag': tag_obj,
            #         'tagged_by': 'admin',
            #         'tagged_at': '2026-05-30 00:03:00'
            #     },
            #     ...
            # ]
        """
        entity_tags = cls.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id
        ).select_related('tag', 'tagged_by')
        
        result = []
        for et in entity_tags:
            result.append({
                'tag': et.tag,
                'tagged_by': et.tagged_by_username or 'System',
                'tagged_at': et.tagged_at.isoformat(),
                'tagged_by_user': et.tagged_by
            })
        
        return result

    @classmethod
    def has_tag(cls, entity_type, entity_id, tag):
        """
        Check if entity has a specific tag
        
        Args:
            entity_type: Entity type
            entity_id: Entity ID
            tag: Tag instance or slug
        
        Returns:
            Boolean
        
        Example:
            if EntityTag.has_tag('bookings', booking.id, tag):
                # Entity has tag
        """
        if isinstance(tag, str):
            # Assume it's a slug
            return cls.objects.filter(
                entity_type=entity_type,
                entity_id=entity_id,
                tag__slug=tag
            ).exists()
        
        return cls.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id,
            tag=tag
        ).exists()

    @classmethod
    def has_any_tag(cls, entity_type, entity_id, tags):
        """
        Check if entity has any of the tags
        
        Args:
            entity_type: Entity type
            entity_id: Entity ID
            tags: List of Tag instances or slugs
        
        Returns:
            Boolean
        
        Example:
            if EntityTag.has_any_tag('bookings', booking.id, [tag1, tag2]):
                # Entity has at least one tag
        """
        tag_ids = []
        tag_slugs = []
        
        for tag in tags:
            if isinstance(tag, str):
                tag_slugs.append(tag)
            else:
                tag_ids.append(tag.id)
        
        return cls.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id
        ).filter(
            Q(tag_id__in=tag_ids) |
            Q(tag__slug__in=tag_slugs)
        ).exists()

    @classmethod
    def has_all_tags(cls, entity_type, entity_id, tags):
        """
        Check if entity has all tags
        
        Args:
            entity_type: Entity type
            entity_id: Entity ID
            tags: List of Tag instances or slugs
        
        Returns:
            Boolean
        
        Example:
            if EntityTag.has_all_tags('bookings', booking.id, [tag1, tag2]):
                # Entity has all tags
        """
        return cls.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id
        ).count() == len(tags)

    # ========================================================================
    # QUERY METHODS - TAGGED ENTITIES
    # ========================================================================

    @classmethod
    def get_tagged_entity_ids(cls, tag, entity_type):
        """
        Get all entity IDs with a specific tag
        
        Args:
            tag: Tag instance
            entity_type: Entity type
        
        Returns:
            List of entity IDs
        
        Example:
            booking_ids = EntityTag.get_tagged_entity_ids(tag, 'bookings')
        """
        return list(
            cls.objects.filter(
                tag=tag,
                entity_type=entity_type
            ).values_list('entity_id', flat=True)
        )

    @classmethod
    def get_tagged_entities_count(cls, tag, entity_type):
        """
        Get count of entities with a tag
        
        Args:
            tag: Tag instance
            entity_type: Entity type
        
        Returns:
            Integer count
        
        Example:
            count = EntityTag.get_tagged_entities_count(tag, 'bookings')
        """
        return cls.objects.filter(
            tag=tag,
            entity_type=entity_type
        ).count()

    @classmethod
    def get_tagged_entities_with_info(cls, tag, entity_type):
        """
        Get tagged entities with tagging info
        
        Args:
            tag: Tag instance
            entity_type: Entity type
        
        Returns:
            List of dicts with entity info
        
        Example:
            entities = EntityTag.get_tagged_entities_with_info(tag, 'bookings')
        """
        entity_tags = cls.objects.filter(
            tag=tag,
            entity_type=entity_type
        ).select_related('tagged_by').order_by('-tagged_at')
        
        result = []
        for et in entity_tags:
            result.append({
                'entity_id': et.entity_id,
                'tagged_by': et.tagged_by_username or 'System',
                'tagged_at': et.tagged_at.isoformat(),
                'tagged_by_user': et.tagged_by
            })
        
        return result

    # ========================================================================
    # QUERY METHODS - COMMON TAGS
    # ========================================================================

    @classmethod
    def get_common_tags(cls, entity_type, entity_ids):
        """
        Get tags common to all entities
        
        Args:
            entity_type: Entity type
            entity_ids: List of entity IDs
        
        Returns:
            QuerySet of Tag objects
        
        Example:
            common_tags = EntityTag.get_common_tags(
                'bookings',
                [booking1.id, booking2.id]
            )
        """
        from tags.models.tags import Tag
        
        return Tag.objects.filter(
            entity_tags__entity_type=entity_type,
            entity_tags__entity_id__in=entity_ids
        ).annotate(
            count=Count('id')
        ).filter(
            count=len(entity_ids)
        ).distinct()

    @classmethod
    def get_tags_with_counts(cls, entity_type):
        """
        Get all tags with usage counts for entity type
        
        Args:
            entity_type: Entity type
        
        Returns:
            List of tuples (Tag, count)
        
        Example:
            tags_with_counts = EntityTag.get_tags_with_counts('bookings')
        """
        from tags.models.tags import Tag
        
        tags = Tag.objects.filter(
            entity_tags__entity_type=entity_type
        ).annotate(
            usage_count=Count('entity_tags')
        ).order_by('-usage_count')
        
        return [(tag, tag.usage_count) for tag in tags]

    # ========================================================================
    # MUTATION METHODS - TAG ENTITY
    # ========================================================================

    @classmethod
    def tag_entity(cls, tag, entity_type, entity_id, tagged_by=None):
        """
        Tag an entity
        
        Args:
            tag: Tag instance
            entity_type: Entity type
            entity_id: Entity ID
            tagged_by: UserAccount instance
        
        Returns:
            Tuple (EntityTag instance, created)
        
        Example:
            entity_tag, created = EntityTag.tag_entity(
                tag=tag,
                entity_type='bookings',
                entity_id=booking.id,
                tagged_by=user
            )
        """
        entity_tag, created = cls.objects.get_or_create(
            tag=tag,
            entity_type=entity_type,
            entity_id=entity_id,
            defaults={
                'tagged_by': tagged_by,
                'tagged_by_username': tagged_by.username if tagged_by else None
            }
        )
        return entity_tag, created

    @classmethod
    def untag_entity(cls, tag, entity_type, entity_id):
        """
        Remove tag from entity
        
        Args:
            tag: Tag instance
            entity_type: Entity type
            entity_id: Entity ID
        
        Returns:
            Number of deleted items
        
        Example:
            count = EntityTag.untag_entity(tag, 'bookings', booking.id)
        """
        count, _ = cls.objects.filter(
            tag=tag,
            entity_type=entity_type,
            entity_id=entity_id
        ).delete()
        return count

    @classmethod
    def bulk_tag_entity(cls, tags, entity_type, entity_id, tagged_by=None):
        """
        Apply multiple tags to entity
        
        Args:
            tags: List of Tag instances
            entity_type: Entity type
            entity_id: Entity ID
            tagged_by: UserAccount instance
        
        Returns:
            List of EntityTag instances
        
        Example:
            entity_tags = EntityTag.bulk_tag_entity(
                tags=[tag1, tag2, tag3],
                entity_type='bookings',
                entity_id=booking.id,
                tagged_by=user
            )
        """
        entity_tags = []
        for tag in tags:
            entity_tag, _ = cls.tag_entity(
                tag=tag,
                entity_type=entity_type,
                entity_id=entity_id,
                tagged_by=tagged_by
            )
            entity_tags.append(entity_tag)
        return entity_tags

    @classmethod
    def bulk_untag_entity(cls, tags, entity_type, entity_id):
        """
        Remove multiple tags from entity
        
        Args:
            tags: List of Tag instances
            entity_type: Entity type
            entity_id: Entity ID
        
        Returns:
            Number of deleted items
        
        Example:
            count = EntityTag.bulk_untag_entity(
                tags=[tag1, tag2],
                entity_type='bookings',
                entity_id=booking.id
            )
        """
        count = 0
        for tag in tags:
            count += cls.untag_entity(tag, entity_type, entity_id)
        return count

    @classmethod
    def clear_entity_tags(cls, entity_type, entity_id):
        """
        Remove all tags from entity
        
        Args:
            entity_type: Entity type
            entity_id: Entity ID
        
        Returns:
            Number of deleted items
        
        Example:
            count = EntityTag.clear_entity_tags('bookings', booking.id)
        """
        count, _ = cls.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id
        ).delete()
        return count

    @classmethod
    def replace_entity_tags(cls, tags, entity_type, entity_id, tagged_by=None):
        """
        Replace all tags for entity
        
        Args:
            tags: List of Tag instances
            entity_type: Entity type
            entity_id: Entity ID
            tagged_by: UserAccount instance
        
        Returns:
            List of EntityTag instances
        
        Example:
            entity_tags = EntityTag.replace_entity_tags(
                tags=[tag1, tag2],
                entity_type='bookings',
                entity_id=booking.id,
                tagged_by=user
            )
        """
        # Clear existing tags
        cls.clear_entity_tags(entity_type, entity_id)
        
        # Apply new tags
        return cls.bulk_tag_entity(tags, entity_type, entity_id, tagged_by)

    # ========================================================================
    # BULK MUTATION METHODS - MULTIPLE ENTITIES
    # ========================================================================

    @classmethod
    def bulk_tag_entities(cls, tag, entity_type, entity_ids, tagged_by=None):
        """
        Apply tag to multiple entities
        
        Args:
            tag: Tag instance
            entity_type: Entity type
            entity_ids: List of entity IDs
            tagged_by: UserAccount instance
        
        Returns:
            List of EntityTag instances
        
        Example:
            entity_tags = EntityTag.bulk_tag_entities(
                tag=tag,
                entity_type='bookings',
                entity_ids=[booking1.id, booking2.id, booking3.id],
                tagged_by=user
            )
        """
        entity_tags = []
        for entity_id in entity_ids:
            entity_tag, _ = cls.tag_entity(
                tag=tag,
                entity_type=entity_type,
                entity_id=entity_id,
                tagged_by=tagged_by
            )
            entity_tags.append(entity_tag)
        return entity_tags

    @classmethod
    def bulk_untag_entities(cls, tag, entity_type, entity_ids):
        """
        Remove tag from multiple entities
        
        Args:
            tag: Tag instance
            entity_type: Entity type
            entity_ids: List of entity IDs
        
        Returns:
            Number of deleted items
        
        Example:
            count = EntityTag.bulk_untag_entities(
                tag=tag,
                entity_type='bookings',
                entity_ids=[booking1.id, booking2.id]
            )
        """
        count, _ = cls.objects.filter(
            tag=tag,
            entity_type=entity_type,
            entity_id__in=entity_ids
        ).delete()
        return count

    # ========================================================================
    # STATISTICS METHODS
    # ========================================================================

    @classmethod
    def get_entity_tag_stats(cls, entity_type, entity_id):
        """
        Get tagging statistics for entity
        
        Args:
            entity_type: Entity type
            entity_id: Entity ID
        
        Returns:
            Dictionary with statistics
        
        Example:
            stats = EntityTag.get_entity_tag_stats('bookings', booking.id)
            # Returns: {
            #     'total_tags': 3,
            #     'tags': ['vip', 'urgent', 'completed'],
            #     'last_tagged_at': '2026-05-30 00:03:00',
            #     'last_tagged_by': 'admin'
            # }
        """
        entity_tags = cls.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id
        ).select_related('tag', 'tagged_by').order_by('-tagged_at')
        
        tags_list = [et.tag.slug for et in entity_tags]
        last_tag = entity_tags.first()
        
        return {
            'total_tags': len(tags_list),
            'tags': tags_list,
            'last_tagged_at': last_tag.tagged_at.isoformat() if last_tag else None,
            'last_tagged_by': last_tag.tagged_by_username if last_tag else None
        }

    @classmethod
    def get_user_tagging_activity(cls, user, days=30):
        """
        Get user's tagging activity
        
        Args:
            user: UserAccount instance
            days: Number of days to look back
        
        Returns:
            Dictionary with activity stats
        
        Example:
            activity = EntityTag.get_user_tagging_activity(user, days=30)
        """
        from django.utils import timezone
        from datetime import timedelta
        
        start_date = timezone.now() - timedelta(days=days)
        
        entity_tags = cls.objects.filter(
            tagged_by=user,
            tagged_at__gte=start_date
        )
        
        # Count by entity type
        by_type = {}
        for et in entity_tags:
            by_type[et.entity_type] = by_type.get(et.entity_type, 0) + 1
        
        return {
            'total_tags': entity_tags.count(),
            'by_entity_type': by_type,
            'period_days': days
        }