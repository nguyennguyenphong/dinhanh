# ============================================================================
# FILE: apps/tags/models.py
# Tag Models with Flexible Tagging Support
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.utils.text import slugify
from django.core.exceptions import ValidationError
import re
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
    
    Use Cases:
    - Categorize vehicles (luxury, economy, family)
    - Categorize bookings (urgent, vip, regular)
    - Categorize employees (driver, mechanic, manager)
    - Categorize trips (express, standard, charter)
    - Categorize documents (important, archived, draft)
    
    Color Palette:
    - Red: #EF4444 (urgent, important)
    - Blue: #3B82F6 (info, standard)
    - Green: #10B981 (success, completed)
    - Yellow: #F59E0B (warning, pending)
    - Purple: #8B5CF6 (premium, vip)
    - Gray: #6B7280 (default, neutral)
    
    Example:
        # Create tag
        tag = Tag.objects.create(
            tenant=tenant,
            slug='vip-customer',
            label='VIP Customer',
            color='#8B5CF6'
        )
        
        # Add tag to entity
        TaggedItem.tag_entity(
            tag=tag,
            entity_type='bookings',
            entity_id=booking.id
        )
        
        # Get tagged items
        items = TaggedItem.get_tagged_items(tag, 'bookings')
    """

    id = models.AutoField(primary_key=True)
    
    # ========================================================================
    # MULTI-TENANT RELATIONSHIP
    # ========================================================================
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='tags',
        db_index=True,
        help_text='Tenant that owns this tag',
        db_comment='Reference to tenant'
    )
    
    # ========================================================================
    # TAG IDENTIFICATION
    # ========================================================================
    
    slug = models.CharField(
        max_length=80,
        validators=[
            RegexValidator(
                regex=r'^[a-z0-9\-]+$',
                message='Slug must contain only lowercase letters, numbers, and hyphens'
            )
        ],
        help_text='URL-friendly identifier (e.g., "vip-customer")',
        db_comment='Tag slug'
    )
    label = models.CharField(
        max_length=100,
        help_text='Human-readable label (e.g., "VIP Customer")',
        db_comment='Tag label'
    )
    
    # ========================================================================
    # DISPLAY
    # ========================================================================
    
    color = models.CharField(
        max_length=7,
        default='#6B7280',
        validators=[
            RegexValidator(
                regex=r'^#[0-9A-Fa-f]{6}$',
                message='Color must be a valid hex color (e.g., #6B7280)'
            )
        ],
        help_text='Hex color code for visual identification',
        db_comment='Tag color'
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='When this tag was created',
        db_comment='Creation timestamp'
    )

    class Meta:
        db_table = 'tags'
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
        ordering = ['label']
        
        # ====================================================================
        # CONSTRAINTS
        # ====================================================================
        
        constraints = [
            # Unique slug per tenant
            models.UniqueConstraint(
                fields=['tenant', 'slug'],
                name='unique_tenant_tag_slug',
                violation_error_message='Tag slug must be unique within tenant'
            ),
        ]
        
        # ====================================================================
        # INDEXES
        # ====================================================================
        
        indexes = [
            # Index for finding tags by tenant
            models.Index(
                fields=['tenant'],
                name='idx_tag_tenant',
                db_comment='Query tags by tenant'
            ),
            # Index for slug lookup
            models.Index(
                fields=['slug'],
                name='idx_tag_slug',
                db_comment='Query tags by slug'
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.label} ({self.tenant.code})"

    def clean(self):
        """
        Validate tag
        """
        # Auto-generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.label)
        
        # Validate slug format
        if not re.match(r'^[a-z0-9\-]+$', self.slug):
            raise ValidationError(
                'Slug must contain only lowercase letters, numbers, and hyphens'
            )

    def save(self, *args, **kwargs):
        """Override save to enforce business rules"""
        self.clean()
        super().save(*args, **kwargs)

    # ========================================================================
    # QUERY METHODS
    # ========================================================================

    @classmethod
    def get_tag(cls, tenant, slug):
        """
        Get tag by slug
        
        Args:
            tenant: Tenant instance
            slug: Tag slug
        
        Returns:
            Tag instance or None
        
        Example:
            tag = Tag.get_tag(tenant, 'vip-customer')
        """
        try:
            return cls.objects.get(tenant=tenant, slug=slug)
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_or_create_tag(cls, tenant, label, slug=None, color='#6B7280'):
        """
        Get or create tag
        
        Args:
            tenant: Tenant instance
            label: Tag label
            slug: Tag slug (auto-generated if not provided)
            color: Tag color
        
        Returns:
            Tuple (Tag instance, created)
        
        Example:
            tag, created = Tag.get_or_create_tag(
                tenant=tenant,
                label='VIP Customer',
                color='#8B5CF6'
            )
        """
        if not slug:
            slug = slugify(label)
        
        tag, created = cls.objects.get_or_create(
            tenant=tenant,
            slug=slug,
            defaults={
                'label': label,
                'color': color
            }
        )
        
        return tag, created

    @classmethod
    def get_all_tags(cls, tenant):
        """
        Get all tags for a tenant
        
        Args:
            tenant: Tenant instance
        
        Returns:
            QuerySet of Tag objects
        """
        return cls.objects.filter(tenant=tenant).order_by('label')

    @classmethod
    def search_tags(cls, tenant, query):
        """
        Search tags by label or slug
        
        Args:
            tenant: Tenant instance
            query: Search query
        
        Returns:
            QuerySet of Tag objects
        
        Example:
            tags = Tag.search_tags(tenant, 'vip')
        """
        from django.db.models import Q
        
        return cls.objects.filter(
            tenant=tenant
        ).filter(
            Q(label__icontains=query) |
            Q(slug__icontains=query)
        ).order_by('label')


class TaggedItem(models.Model):
    """
    Through model for tagging entities
    
    Features:
    - Generic tagging: Tag any entity type
    - Bulk operations: Batch tag/untag
    - Query support: Find items by tags
    - Audit trail: Track tagging changes
    
    Example:
        # Tag an entity
        tagged = TaggedItem.objects.create(
            tag=tag,
            entity_type='bookings',
            entity_id=booking.id
        )
        
        # Get all tags for entity
        tags = TaggedItem.get_entity_tags('bookings', booking.id)
        
        # Get all items with tag
        items = TaggedItem.get_tagged_items(tag, 'bookings')
    """

    id = models.BigAutoField(primary_key=True)
    
    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================
    
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='tagged_items',
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
        help_text='Type of entity being tagged',
        db_comment='Entity type'
    )
    entity_id = models.IntegerField(
        db_index=True,
        help_text='ID of entity being tagged',
        db_comment='Entity ID'
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='When this tag was applied',
        db_comment='Creation timestamp'
    )

    class Meta:
        db_table = 'tagged_items'
        verbose_name = _('Tagged Item')
        verbose_name_plural = _('Tagged Items')
        ordering = ['-created_at']
        
        # ====================================================================
        # CONSTRAINTS
        # ====================================================================
        
        constraints = [
            # Unique tag per entity
            models.UniqueConstraint(
                fields=['tag', 'entity_type', 'entity_id'],
                name='unique_tag_entity',
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
                name='idx_tagged_entity',
                db_comment='Query tags by entity'
            ),
            # Index for finding entities with tag
            models.Index(
                fields=['tag', 'entity_type'],
                name='idx_tagged_tag_type',
                db_comment='Query entities by tag and type'
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.tag.label} on {self.entity_type}#{self.entity_id}"

    # ========================================================================
    # QUERY METHODS
    # ========================================================================

    @classmethod
    def tag_entity(cls, tag, entity_type, entity_id):
        """
        Tag an entity
        
        Args:
            tag: Tag instance
            entity_type: Entity type
            entity_id: Entity ID
        
        Returns:
            Tuple (TaggedItem instance, created)
        
        Example:
            tagged, created = TaggedItem.tag_entity(
                tag=tag,
                entity_type='bookings',
                entity_id=booking.id
            )
        """
        tagged, created = cls.objects.get_or_create(
            tag=tag,
            entity_type=entity_type,
            entity_id=entity_id
        )
        return tagged, created

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
            count = TaggedItem.untag_entity(
                tag=tag,
                entity_type='bookings',
                entity_id=booking.id
            )
        """
        count, _ = cls.objects.filter(
            tag=tag,
            entity_type=entity_type,
            entity_id=entity_id
        ).delete()
        return count

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
            tags = TaggedItem.get_entity_tags('bookings', booking.id)
        """
        return Tag.objects.filter(
            tagged_items__entity_type=entity_type,
            tagged_items__entity_id=entity_id
        ).distinct()

    @classmethod
    def get_tagged_items(cls, tag, entity_type=None):
        """
        Get all items with a tag
        
        Args:
            tag: Tag instance
            entity_type: Optional entity type filter
        
        Returns:
            QuerySet of TaggedItem objects
        
        Example:
            items = TaggedItem.get_tagged_items(tag, 'bookings')
        """
        query = cls.objects.filter(tag=tag)
        
        if entity_type:
            query = query.filter(entity_type=entity_type)
        
        return query.order_by('-created_at')

    @classmethod
    def get_entity_ids_with_tag(cls, tag, entity_type):
        """
        Get list of entity IDs with a tag
        
        Args:
            tag: Tag instance
            entity_type: Entity type
        
        Returns:
            List of entity IDs
        
        Example:
            booking_ids = TaggedItem.get_entity_ids_with_tag(tag, 'bookings')
        """
        return list(
            cls.objects.filter(
                tag=tag,
                entity_type=entity_type
            ).values_list('entity_id', flat=True)
        )

    @classmethod
    def bulk_tag(cls, tags, entity_type, entity_id):
        """
        Apply multiple tags to entity
        
        Args:
            tags: List of Tag instances
            entity_type: Entity type
            entity_id: Entity ID
        
        Returns:
            List of TaggedItem instances
        
        Example:
            tagged = TaggedItem.bulk_tag(
                tags=[tag1, tag2, tag3],
                entity_type='bookings',
                entity_id=booking.id
            )
        """
        tagged_items = []
        for tag in tags:
            tagged, _ = cls.tag_entity(tag, entity_type, entity_id)
            tagged_items.append(tagged)
        return tagged_items

    @classmethod
    def bulk_untag(cls, tags, entity_type, entity_id):
        """
        Remove multiple tags from entity
        
        Args:
            tags: List of Tag instances
            entity_type: Entity type
            entity_id: Entity ID
        
        Returns:
            Number of deleted items
        
        Example:
            count = TaggedItem.bulk_untag(
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
            count = TaggedItem.clear_entity_tags('bookings', booking.id)
        """
        count, _ = cls.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id
        ).delete()
        return count

    @classmethod
    def get_common_tags(cls, entity_type, entity_ids):
        """
        Get tags common to multiple entities
        
        Args:
            entity_type: Entity type
            entity_ids: List of entity IDs
        
        Returns:
            QuerySet of Tag objects
        
        Example:
            common_tags = TaggedItem.get_common_tags(
                'bookings',
                [booking1.id, booking2.id]
            )
        """
        from django.db.models import Count
        
        return Tag.objects.filter(
            tagged_items__entity_type=entity_type,
            tagged_items__entity_id__in=entity_ids
        ).annotate(
            count=Count('id')
        ).filter(
            count=len(entity_ids)
        ).distinct()

    @classmethod
    def get_tags_with_counts(cls, tenant, entity_type=None):
        """
        Get tags with usage counts
        
        Args:
            tenant: Tenant instance
            entity_type: Optional entity type filter
        
        Returns:
            List of tuples (Tag, count)
        
        Example:
            tags_with_counts = TaggedItem.get_tags_with_counts(
                tenant, 'bookings'
            )
        """
        from django.db.models import Count
        
        query = Tag.objects.filter(tenant=tenant).annotate(
            usage_count=Count('tagged_items')
        ).order_by('-usage_count')
        
        if entity_type:
            query = query.filter(
                tagged_items__entity_type=entity_type
            ).distinct()
        
        return [(tag, tag.usage_count) for tag in query]