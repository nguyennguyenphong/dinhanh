# ============================================================================
# FILE: apps/comments/models.py
# Comment Models with Threading and Visibility
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q, Prefetch
from tenants.models.tenants import Tenant


class Comment(models.Model):
    """
    Comment model for entity discussions
    
    Features:
    - Multi-tenant support: Each tenant has own comments
    - Entity linking: Comment on any entity type
    - Nested replies: Support for threaded conversations
    - Visibility control: Internal vs customer-visible
    - Pinning: Pin important comments
    - Edit tracking: Track when comments are edited
    - Author tracking: Track who commented
    - Bulk operations: Batch update comments
    - Query optimization: Efficient queries with prefetch
    
    Entity Types:
    - trips: Trip comments
    - bookings: Booking comments
    - vehicles: Vehicle comments
    - employees: Employee comments
    - invoices: Invoice comments
    - consignments: Consignment comments
    - documents: Document comments
    - custom: Custom entity types
    
    Visibility:
    - is_internal=True: Only visible to staff
    - is_internal=False: Visible to customers
    
    Threading:
    - parent_id=None: Top-level comment
    - parent_id!=None: Reply to comment
    
    Example:
        # Create comment
        comment = Comment.objects.create(
            tenant=tenant,
            entity_type='trips',
            entity_id=trip.id,
            body='Trip completed successfully',
            author=user,
            is_internal=False
        )
        
        # Reply to comment
        reply = Comment.objects.create(
            tenant=tenant,
            entity_type='trips',
            entity_id=trip.id,
            parent=comment,
            body='Thanks for the update',
            author=user
        )
        
        # Get comments with replies
        comments = Comment.get_entity_comments('trips', trip.id)
        
        # Get thread
        thread = comment.get_thread()
    """

    id = models.BigAutoField(primary_key=True)
    
    # ========================================================================
    # MULTI-TENANT RELATIONSHIP
    # ========================================================================
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='comments',
        db_index=True,
        help_text='Tenant that owns this comment'
    )
    
    # ========================================================================
    # ENTITY LINKING
    # ========================================================================
    
    entity_type = models.CharField(
        max_length=60,
        db_index=True,
        help_text='Type of entity being commented on'
    )
    
    entity_id = models.BigIntegerField(
        db_index=True,
        help_text='ID of entity being commented on'
    )
    
    # ========================================================================
    # THREADING
    # ========================================================================
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        db_index=True,
        help_text='Parent comment (for nested replies)'
    )
    
    # ========================================================================
    # COMMENT CONTENT
    # ========================================================================
    
    body = models.TextField(
        help_text='Comment text'
    )
    
    # ========================================================================
    # AUTHOR INFORMATION
    # ========================================================================
    
    author = models.ForeignKey(
        'accounts.UserAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comments',
        help_text='User who wrote this comment'
    )
    
    # ========================================================================
    # VISIBILITY AND PINNING
    # ========================================================================
    
    is_internal = models.BooleanField(
        default=True,
        db_index=True,
        help_text='Comment is internal (staff only)'
    )
    
    is_pinned = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Comment is pinned to top'
    )
    
    # ========================================================================
    # EDIT TRACKING
    # ========================================================================
    
    edited_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When comment was last edited'
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='When comment was created'
    )

    class Meta:
        db_table = 'comments'
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
        ordering = ['-is_pinned', '-created_at']
        
        # ====================================================================
        # INDEXES
        # ====================================================================
        
        indexes = [
            # Index for finding comments by entity
            models.Index(
                fields=['entity_type', 'entity_id'],
                name='idx_comments_entity'
            ),
            # Index for finding replies
            models.Index(
                fields=['parent_id'],
                condition=Q(parent_id__isnull=False),
                name='idx_comments_parent'
            ),
            # Index for finding internal comments
            models.Index(
                fields=['is_internal'],
                name='idx_comments_internal'
            ),
            # Index for finding pinned comments
            models.Index(
                fields=['is_pinned'],
                name='idx_comments_pinned'
            ),
            # Index for author queries
            models.Index(
                fields=['author_id'],
                name='idx_comments_author'
            ),
        ]

    def __str__(self):
        """String representation"""
        preview = self.body[:50] + '...' if len(self.body) > 50 else self.body
        return f"{self.entity_type}#{self.entity_id}: {preview}"

    def clean(self):
        """Validate comment"""
        if not self.body or not self.body.strip():
            raise ValidationError('Comment body cannot be empty')

    def save(self, *args, **kwargs):
        """Override save to enforce business rules"""
        self.clean()
        super().save(*args, **kwargs)

    # ========================================================================
    # EDIT METHODS
    # ========================================================================

    def edit(self, new_body):
        """
        Edit comment
        
        Args:
            new_body: New comment text
        
        Example:
            comment.edit('Updated comment text')
        """
        self.body = new_body
        self.edited_at = timezone.now()
        self.save()

    def is_edited(self):
        """
        Check if comment was edited
        
        Returns:
            Boolean
        
        Example:
            if comment.is_edited():
                # Show edited indicator
        """
        return self.edited_at is not None

    def get_edit_status(self):
        """
        Get edit status display
        
        Returns:
            String
        
        Example:
            status = comment.get_edit_status()
            # Returns: "Edited 2 hours ago" or "Never edited"
        """
        if not self.edited_at:
            return "Never edited"
        
        from django.utils.timesince import timesince
        return f"Edited {timesince(self.edited_at)} ago"

    # ========================================================================
    # PINNING METHODS
    # ========================================================================

    def pin(self):
        """
        Pin comment
        
        Example:
            comment.pin()
        """
        self.is_pinned = True
        self.save()

    def unpin(self):
        """
        Unpin comment
        
        Example:
            comment.unpin()
        """
        self.is_pinned = False
        self.save()

    def toggle_pin(self):
        """
        Toggle pin status
        
        Example:
            comment.toggle_pin()
        """
        self.is_pinned = not self.is_pinned
        self.save()

    # ========================================================================
    # VISIBILITY METHODS
    # ========================================================================

    def make_internal(self):
        """
        Make comment internal (staff only)
        
        Example:
            comment.make_internal()
        """
        self.is_internal = True
        self.save()

    def make_public(self):
        """
        Make comment public (visible to customers)
        
        Example:
            comment.make_public()
        """
        self.is_internal = False
        self.save()

    def is_visible_to_user(self, user):
        """
        Check if comment is visible to user
        
        Args:
            user: UserAccount instance
        
        Returns:
            Boolean
        
        Example:
            if comment.is_visible_to_user(user):
                # Show comment
        """
        # Internal comments only visible to staff
        if self.is_internal:
            return user.is_staff or user.is_superuser
        
        # Public comments visible to everyone
        return True

    # ========================================================================
    # THREADING METHODS
    # ========================================================================

    def reply(self, body, author, is_internal=True):
        """
        Create reply to this comment
        
        Args:
            body: Reply text
            author: UserAccount instance
            is_internal: Internal flag
        
        Returns:
            Comment instance
        
        Example:
            reply = comment.reply('Thanks!', user)
        """
        return Comment.objects.create(
            tenant=self.tenant,
            entity_type=self.entity_type,
            entity_id=self.entity_id,
            parent=self,
            body=body,
            author=author,
            is_internal=is_internal
        )

    def get_replies(self, visible_to_user=None):
        """
        Get replies to this comment
        
        Args:
            visible_to_user: Optional user for visibility filtering
        
        Returns:
            QuerySet of Comment objects
        
        Example:
            replies = comment.get_replies(visible_to_user=user)
        """
        replies = self.replies.all().order_by('created_at')
        
        if visible_to_user:
            # Filter by visibility
            if not (visible_to_user.is_staff or visible_to_user.is_superuser):
                replies = replies.filter(is_internal=False)
        
        return replies

    def get_reply_count(self):
        """
        Get number of replies
        
        Returns:
            Integer
        
        Example:
            count = comment.get_reply_count()
        """
        return self.replies.count()

    def get_thread(self):
        """
        Get entire thread (parent and all replies)
        
        Returns:
            List of Comment objects
        
        Example:
            thread = comment.get_thread()
        """
        thread = [self]
        thread.extend(list(self.get_replies()))
        return thread

    def get_root_comment(self):
        """
        Get root comment of thread
        
        Returns:
            Comment instance
        
        Example:
            root = comment.get_root_comment()
        """
        if self.parent:
            return self.parent.get_root_comment()
        return self

    def is_root(self):
        """
        Check if comment is root (not a reply)
        
        Returns:
            Boolean
        
        Example:
            if comment.is_root():
                # This is a top-level comment
        """
        return self.parent is None

    # ========================================================================
    # QUERY METHODS
    # ========================================================================

    @classmethod
    def get_entity_comments(cls, entity_type, entity_id, visible_to_user=None):
        """
        Get all comments for entity
        
        Args:
            entity_type: Entity type
            entity_id: Entity ID
            visible_to_user: Optional user for visibility filtering
        
        Returns:
            QuerySet of Comment objects (root comments only)
        
        Example:
            comments = Comment.get_entity_comments('trips', trip.id)
        """
        query = cls.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id,
            parent__isnull=True  # Only root comments
        ).order_by('-is_pinned', '-created_at')
        
        if visible_to_user:
            # Filter by visibility
            if not (visible_to_user.is_staff or visible_to_user.is_superuser):
                query = query.filter(is_internal=False)
        
        return query

    @classmethod
    def get_entity_comments_with_replies(cls, entity_type, entity_id, visible_to_user=None):
        """
        Get comments with replies using prefetch
        
        Args:
            entity_type: Entity type
            entity_id: Entity ID
            visible_to_user: Optional user for visibility filtering
        
        Returns:
            QuerySet of Comment objects with prefetched replies
        
        Example:
            comments = Comment.get_entity_comments_with_replies('trips', trip.id)
        """
        # Prefetch replies
        replies_prefetch = Prefetch(
            'replies',
            queryset=cls.objects.all().order_by('created_at')
        )
        
        query = cls.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id,
            parent__isnull=True
        ).prefetch_related(replies_prefetch).order_by('-is_pinned', '-created_at')
        
        if visible_to_user:
            if not (visible_to_user.is_staff or visible_to_user.is_superuser):
                query = query.filter(is_internal=False)
        
        return query

    @classmethod
    def get_author_comments(cls, author, entity_type=None):
        """
        Get comments by author
        
        Args:
            author: UserAccount instance
            entity_type: Optional entity type filter
        
        Returns:
            QuerySet of Comment objects
        
        Example:
            comments = Comment.get_author_comments(user, 'trips')
        """
        query = cls.objects.filter(author=author).order_by('-created_at')
        
        if entity_type:
            query = query.filter(entity_type=entity_type)
        
        return query

    @classmethod
    def get_recent_comments(cls, tenant, limit=10):
        """
        Get recent comments
        
        Args:
            tenant: Tenant instance
            limit: Maximum number of comments
        
        Returns:
            QuerySet of Comment objects
        
        Example:
            recent = Comment.get_recent_comments(tenant, limit=20)
        """
        return cls.objects.filter(
            tenant=tenant,
            parent__isnull=True
        ).order_by('-created_at')[:limit]

    @classmethod
    def get_pinned_comments(cls, entity_type, entity_id):
        """
        Get pinned comments for entity
        
        Args:
            entity_type: Entity type
            entity_id: Entity ID
        
        Returns:
            QuerySet of Comment objects
        
        Example:
            pinned = Comment.get_pinned_comments('trips', trip.id)
        """
        return cls.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id,
            is_pinned=True,
            parent__isnull=True
        ).order_by('-created_at')

    @classmethod
    def get_internal_comments(cls, entity_type, entity_id):
        """
        Get internal comments for entity
        
        Args:
            entity_type: Entity type
            entity_id: Entity ID
        
        Returns:
            QuerySet of Comment objects
        
        Example:
            internal = Comment.get_internal_comments('trips', trip.id)
        """
        return cls.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id,
            is_internal=True,
            parent__isnull=True
        ).order_by('-created_at')

    @classmethod
    def get_public_comments(cls, entity_type, entity_id):
        """
        Get public comments for entity
        
        Args:
            entity_type: Entity type
            entity_id: Entity ID
        
        Returns:
            QuerySet of Comment objects
        
        Example:
            public = Comment.get_public_comments('trips', trip.id)
        """
        return cls.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id,
            is_internal=False,
            parent__isnull=True
        ).order_by('-created_at')

    # ========================================================================
    # STATISTICS METHODS
    # ========================================================================

    @classmethod
    def get_entity_comment_count(cls, entity_type, entity_id):
        """
        Get total comment count for entity
        
        Args:
            entity_type: Entity type
            entity_id: Entity ID
        
        Returns:
            Integer
        
        Example:
            count = Comment.get_entity_comment_count('trips', trip.id)
        """
        return cls.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id
        ).count()

    @classmethod
    def get_entity_statistics(cls, entity_type, entity_id):
        """
        Get comment statistics for entity
        
        Args:
            entity_type: Entity type
            entity_id: Entity ID
        
        Returns:
            Dictionary with statistics
        
        Example:
            stats = Comment.get_entity_statistics('trips', trip.id)
        """
        comments = cls.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id
        )
        
        total = comments.count()
        root = comments.filter(parent__isnull=True).count()
        replies = comments.filter(parent__isnull=False).count()
        internal = comments.filter(is_internal=True).count()
        public = comments.filter(is_internal=False).count()
        pinned = comments.filter(is_pinned=True).count()
        
        return {
            'total': total,
            'root_comments': root,
            'replies': replies,
            'internal': internal,
            'public': public,
            'pinned': pinned
        }

    @classmethod
    def get_author_statistics(cls, author):
        """
        Get comment statistics for author
        
        Args:
            author: UserAccount instance
        
        Returns:
            Dictionary with statistics
        
        Example:
            stats = Comment.get_author_statistics(user)
        """
        comments = cls.objects.filter(author=author)
        
        total = comments.count()
        root = comments.filter(parent__isnull=True).count()
        replies = comments.filter(parent__isnull=False).count()
        
        return {
            'total': total,
            'root_comments': root,
            'replies': replies
        }

    # ========================================================================
    # BULK OPERATION METHODS
    # ========================================================================

    @classmethod
    def bulk_make_internal(cls, comment_ids):
        """
        Bulk make comments internal
        
        Args:
            comment_ids: List of comment IDs
        
        Returns:
            Number of updated comments
        
        Example:
            count = Comment.bulk_make_internal([1, 2, 3])
        """
        return cls.objects.filter(id__in=comment_ids).update(
            is_internal=True
        )

    @classmethod
    def bulk_make_public(cls, comment_ids):
        """
        Bulk make comments public
        
        Args:
            comment_ids: List of comment IDs
        
        Returns:
            Number of updated comments
        
        Example:
            count = Comment.bulk_make_public([1, 2, 3])
        """
        return cls.objects.filter(id__in=comment_ids).update(
            is_internal=False
        )

    @classmethod
    def bulk_pin(cls, comment_ids):
        """
        Bulk pin comments
        
        Args:
            comment_ids: List of comment IDs
        
        Returns:
            Number of updated comments
        
        Example:
            count = Comment.bulk_pin([1, 2, 3])
        """
        return cls.objects.filter(id__in=comment_ids).update(
            is_pinned=True
        )

    @classmethod
    def bulk_unpin(cls, comment_ids):
        """
        Bulk unpin comments
        
        Args:
            comment_ids: List of comment IDs
        
        Returns:
            Number of updated comments
        
        Example:
            count = Comment.bulk_unpin([1, 2, 3])
        """
        return cls.objects.filter(id__in=comment_ids).update(
            is_pinned=False
        )

    @classmethod
    def bulk_delete_by_entity(cls, entity_type, entity_id):
        """
        Bulk delete comments for entity
        
        Args:
            entity_type: Entity type
            entity_id: Entity ID
        
        Returns:
            Number of deleted comments
        
        Example:
            count = Comment.bulk_delete_by_entity('trips', trip.id)
        """
        count, _ = cls.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id
        ).delete()
        return count