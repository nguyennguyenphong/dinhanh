# ============================================================================
# FILE: apps/core/models.py
# System Config History Models with Versioning
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import difflib
from datetime import timedelta
from system_config.models.system_configs import SystemConfig


class SystemConfigHistory(models.Model):
    """
    System configuration history model for tracking changes over time
    
    Features:
    - Complete version history: Track all changes to configs
    - Change tracking: Store old and new values
    - Audit trail: Record who made changes and when
    - Diff support: Generate diffs between versions
    - Rollback support: Revert to previous versions
    - Retention policy: Automatic cleanup of old history
    - Change comparison: Compare multiple versions
    - Change analysis: Analyze change patterns
    
    Use Cases:
    - Compliance audits: Track all configuration changes
    - Troubleshooting: Identify when issues started
    - Rollback: Revert to previous configuration
    - Change analysis: Understand configuration evolution
    - Security: Detect unauthorized changes
    
    Example:
        # Create history entry
        history = SystemConfigHistory.objects.create(
            config=config,
            old_value='old_value',
            new_value='new_value',
            changed_by=user
        )
        
        # Get change history
        history = SystemConfigHistory.get_history(config)
        
        # Get diff
        diff = history.get_diff()
        
        # Rollback to version
        SystemConfigHistory.rollback_to_version(config, version_id)
    """

    id = models.BigAutoField(primary_key=True)
    
    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================
    
    config = models.ForeignKey(
        SystemConfig,
        on_delete=models.CASCADE,
        related_name='history',
        db_index=True,
        help_text='Configuration that was changed',
        db_comment='Reference to system config'
    )
    
    # ========================================================================
    # CHANGE DETAILS
    # ========================================================================
    
    old_value = models.TextField(
        blank=True,
        null=True,
        help_text='Previous value before change',
        db_comment='Old value'
    )
    new_value = models.TextField(
        blank=True,
        null=True,
        help_text='New value after change',
        db_comment='New value'
    )
    
    # ========================================================================
    # AUDIT INFORMATION
    # ========================================================================
    
    changed_by = models.ForeignKey(
        'accounts.UserAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='config_history_changes',
        help_text='User who made the change',
        db_comment='Changed by user'
    )
    changed_by_username = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        help_text='Username snapshot at time of change',
        db_comment='Username snapshot'
    )
    
    # ========================================================================
    # METADATA
    # ========================================================================
    
    reason = models.TextField(
        blank=True,
        null=True,
        help_text='Reason for the change',
        db_comment='Change reason'
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    changed_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='When the change was made',
        db_comment='Change timestamp'
    )

    class Meta:
        db_table = 'system_config_history'
        verbose_name = _('System Config History')
        verbose_name_plural = _('System Config Histories')
        ordering = ['-changed_at']
        
        # ====================================================================
        # INDEXES
        # ====================================================================
        
        indexes = [
            # Index for finding history by config
            models.Index(
                fields=['config', 'changed_at'],
                name='idx_config_history_config_changed',
                db_comment='Query history by config and date'
            ),
            # Index for finding changes by user
            models.Index(
                fields=['changed_by', 'changed_at'],
                name='idx_config_history_user_changed',
                db_comment='Query changes by user and date'
            ),
            # Index for time range queries
            models.Index(
                fields=['-changed_at'],
                name='idx_config_history_changed_desc',
                db_comment='Query history by date descending'
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.config.key} - {self.changed_at.strftime('%Y-%m-%d %H:%M:%S')}"

    def save(self, *args, **kwargs):
        """Override save to capture username"""
        if self.changed_by and not self.changed_by_username:
            self.changed_by_username = self.changed_by.username
        super().save(*args, **kwargs)

    # ========================================================================
    # DIFF METHODS
    # ========================================================================

    def get_diff(self):
        """
        Get diff between old and new values
        
        Returns:
            List of diff lines
        
        Example:
            diff = history.get_diff()
            # Returns: ['- old_value', '+ new_value']
        """
        old_lines = (self.old_value or '').splitlines(keepends=True)
        new_lines = (self.new_value or '').splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f'{self.config.key} (old)',
            tofile=f'{self.config.key} (new)',
            lineterm=''
        )
        
        return list(diff)

    def get_diff_html(self):
        """
        Get HTML formatted diff
        
        Returns:
            HTML string with colored diff
        """
        diff = self.get_diff()
        html = '<pre style="background-color: #f5f5f5; padding: 10px; border-radius: 3px;">'
        
        for line in diff:
            if line.startswith('-'):
                html += f'<span style="color: #d32f2f;">{line}</span>\n'
            elif line.startswith('+'):
                html += f'<span style="color: #388e3c;">{line}</span>\n'
            else:
                html += f'{line}\n'
        
        html += '</pre>'
        return html

    def has_changes(self):
        """
        Check if there are actual changes
        
        Returns:
            Boolean
        """
        return self.old_value != self.new_value

    def get_change_summary(self):
        """
        Get summary of changes
        
        Returns:
            Dictionary with change summary
        
        Example:
            summary = history.get_change_summary()
            # Returns: {
            #     'field': 'key',
            #     'old': 'old_value',
            #     'new': 'new_value',
            #     'changed_by': 'admin',
            #     'changed_at': '2026-05-29 23:54:00'
            # }
        """
        return {
            'field': self.config.key,
            'category': self.config.category,
            'old': self.old_value,
            'new': self.new_value,
            'changed_by': self.changed_by_username,
            'changed_at': self.changed_at.isoformat(),
            'reason': self.reason
        }

    # ========================================================================
    # QUERY METHODS
    # ========================================================================

    @classmethod
    def get_history(cls, config, limit=None):
        """
        Get change history for a config
        
        Args:
            config: SystemConfig instance
            limit: Maximum number of records
        
        Returns:
            QuerySet of SystemConfigHistory objects
        
        Example:
            history = SystemConfigHistory.get_history(config)
        """
        query = cls.objects.filter(config=config).order_by('-changed_at')
        
        if limit:
            query = query[:limit]
        
        return query

    @classmethod
    def get_history_for_period(cls, config, start_date, end_date):
        """
        Get change history for a date range
        
        Args:
            config: SystemConfig instance
            start_date: Start date
            end_date: End date
        
        Returns:
            QuerySet of SystemConfigHistory objects
        
        Example:
            history = SystemConfigHistory.get_history_for_period(
                config,
                timezone.now() - timedelta(days=30),
                timezone.now()
            )
        """
        return cls.objects.filter(
            config=config,
            changed_at__gte=start_date,
            changed_at__lte=end_date
        ).order_by('-changed_at')

    @classmethod
    def get_history_by_user(cls, config, user):
        """
        Get changes made by a specific user
        
        Args:
            config: SystemConfig instance
            user: UserAccount instance
        
        Returns:
            QuerySet of SystemConfigHistory objects
        """
        return cls.objects.filter(
            config=config,
            changed_by=user
        ).order_by('-changed_at')

    @classmethod
    def get_recent_changes(cls, tenant, days=7):
        """
        Get recent changes for a tenant
        
        Args:
            tenant: Tenant instance
            days: Number of days to look back
        
        Returns:
            QuerySet of SystemConfigHistory objects
        
        Example:
            recent = SystemConfigHistory.get_recent_changes(tenant, days=7)
        """
        start_date = timezone.now() - timedelta(days=days)
        
        return cls.objects.filter(
            config__tenant=tenant,
            changed_at__gte=start_date
        ).order_by('-changed_at')

    @classmethod
    def get_version_at_time(cls, config, timestamp):
        """
        Get config value at a specific time
        
        Args:
            config: SystemConfig instance
            timestamp: Datetime to query
        
        Returns:
            SystemConfigHistory instance or None
        
        Example:
            version = SystemConfigHistory.get_version_at_time(
                config,
                timezone.now() - timedelta(days=7)
            )
        """
        return cls.objects.filter(
            config=config,
            changed_at__lte=timestamp
        ).order_by('-changed_at').first()

    @classmethod
    def get_version_number(cls, config, history_id):
        """
        Get version number of a history entry
        
        Args:
            config: SystemConfig instance
            history_id: History entry ID
        
        Returns:
            Version number (1-based)
        """
        count = cls.objects.filter(
            config=config,
            id__gte=history_id
        ).count()
        
        return count

    # ========================================================================
    # ROLLBACK METHODS
    # ========================================================================

    @classmethod
    def rollback_to_version(cls, config, history_id, rolled_back_by=None, reason=None):
        """
        Rollback config to a previous version
        
        Args:
            config: SystemConfig instance
            history_id: History entry ID to rollback to
            rolled_back_by: UserAccount instance
            reason: Reason for rollback
        
        Returns:
            SystemConfigHistory instance (new history entry)
        
        Raises:
            ValueError: If history not found
        
        Example:
            history = SystemConfigHistory.rollback_to_version(
                config,
                history_id=123,
                rolled_back_by=admin_user,
                reason='Reverting to previous version'
            )
        """
        try:
            target_history = cls.objects.get(id=history_id, config=config)
        except cls.DoesNotExist:
            raise ValueError(f'History entry {history_id} not found')
        
        # Store current value as old
        old_value = config.value
        
        # Restore old value
        config.value = target_history.old_value
        config.updated_by = rolled_back_by
        config.save()
        
        # Create new history entry for rollback
        rollback_history = cls.objects.create(
            config=config,
            old_value=old_value,
            new_value=target_history.old_value,
            changed_by=rolled_back_by,
            changed_by_username=rolled_back_by.username if rolled_back_by else None,
            reason=f'Rollback to version {history_id}: {reason or ""}'
        )
        
        return rollback_history

    @classmethod
    def rollback_to_time(cls, config, timestamp, rolled_back_by=None, reason=None):
        """
        Rollback config to value at a specific time
        
        Args:
            config: SystemConfig instance
            timestamp: Datetime to rollback to
            rolled_back_by: UserAccount instance
            reason: Reason for rollback
        
        Returns:
            SystemConfigHistory instance (new history entry)
        
        Example:
            history = SystemConfigHistory.rollback_to_time(
                config,
                timezone.now() - timedelta(days=7),
                rolled_back_by=admin_user
            )
        """
        target_history = cls.get_version_at_time(config, timestamp)
        
        if not target_history:
            raise ValueError(f'No history found before {timestamp}')
        
        return cls.rollback_to_version(
            config,
            target_history.id,
            rolled_back_by=rolled_back_by,
            reason=reason
        )

    # ========================================================================
    # COMPARISON METHODS
    # ========================================================================

    @classmethod
    def compare_versions(cls, history1_id, history2_id):
        """
        Compare two versions
        
        Args:
            history1_id: First history entry ID
            history2_id: Second history entry ID
        
        Returns:
            Dictionary with comparison
        
        Example:
            comparison = SystemConfigHistory.compare_versions(
                history1_id=100,
                history2_id=200
            )
        """
        try:
            h1 = cls.objects.get(id=history1_id)
            h2 = cls.objects.get(id=history2_id)
        except cls.DoesNotExist:
            raise ValueError('One or both history entries not found')
        
        old_lines = (h1.new_value or '').splitlines(keepends=True)
        new_lines = (h2.new_value or '').splitlines(keepends=True)
        
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f'Version {h1.id}',
            tofile=f'Version {h2.id}',
            lineterm=''
        ))
        
        return {
            'version1': h1.get_change_summary(),
            'version2': h2.get_change_summary(),
            'diff': diff,
            'has_changes': h1.new_value != h2.new_value
        }

    # ========================================================================
    # ANALYSIS METHODS
    # ========================================================================

    @classmethod
    def get_change_frequency(cls, config, days=30):
        """
        Get change frequency statistics
        
        Args:
            config: SystemConfig instance
            days: Number of days to analyze
        
        Returns:
            Dictionary with statistics
        
        Example:
            stats = SystemConfigHistory.get_change_frequency(config, days=30)
            # Returns: {
            #     'total_changes': 5,
            #     'by_user': {'admin': 3, 'user1': 2},
            #     'average_per_day': 0.17
            # }
        """
        start_date = timezone.now() - timedelta(days=days)
        
        history = cls.objects.filter(
            config=config,
            changed_at__gte=start_date
        )
        
        total = history.count()
        
        # Count by user
        by_user = {}
        for entry in history:
            username = entry.changed_by_username or 'System'
            by_user[username] = by_user.get(username, 0) + 1
        
        return {
            'total_changes': total,
            'by_user': by_user,
            'average_per_day': total / days if days > 0 else 0
        }

    @classmethod
    def get_most_changed_configs(cls, tenant, limit=10, days=30):
        """
        Get most frequently changed configs
        
        Args:
            tenant: Tenant instance
            limit: Maximum number of configs
            days: Number of days to analyze
        
        Returns:
            List of tuples (config, change_count)
        
        Example:
            most_changed = SystemConfigHistory.get_most_changed_configs(
                tenant, limit=10, days=30
            )
        """
        from django.db.models import Count
        
        start_date = timezone.now() - timedelta(days=days)
        
        configs = cls.objects.filter(
            config__tenant=tenant,
            changed_at__gte=start_date
        ).values('config').annotate(
            count=Count('id')
        ).order_by('-count')[:limit]
        
        result = []
        for item in configs:
            config = SystemConfig.objects.get(id=item['config'])
            result.append((config, item['count']))
        
        return result

    @classmethod
    def cleanup_old_history(cls, days=365):
        """
        Delete history entries older than specified days
        
        Args:
            days: Delete entries older than this many days
        
        Returns:
            Number of deleted entries
        
        Example:
            deleted = SystemConfigHistory.cleanup_old_history(days=365)
        """
        cutoff_date = timezone.now() - timedelta(days=days)
        
        old_history = cls.objects.filter(changed_at__lt=cutoff_date)
        count = old_history.count()
        old_history.delete()
        
        return count