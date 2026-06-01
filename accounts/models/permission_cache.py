from django.db import models
from django.utils.translation import gettext_lazy as _

class PermissionCache(models.Model):
    """
    Cache layer for permission lookups to improve performance

    Features:
    - Cache permission results per user/role
    - Invalidate cache on permission changes
    - Reduce database queries

    Note: This is optional and can be managed via Redis instead
    """

    id = models.AutoField(primary_key=True)

    # Cache key
    cache_key = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text='Cache key (e.g., "user_123_permissions")',
    )

    # Cached data
    permissions = models.JSONField(help_text="Cached permission data")

    # Expiration
    expires_at = models.DateTimeField(help_text="When this cache entry expires")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "permission_cache"
        verbose_name = _("Permission Cache")
        verbose_name_plural = _("Permission Caches")
        ordering = ["-created_at"]

    def __str__(self):
        return self.cache_key

    def is_expired(self):
        """
        Check if cache entry has expired
        """
        from django.utils import timezone

        return timezone.now() > self.expires_at