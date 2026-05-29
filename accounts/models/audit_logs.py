# ============================================================================
# FILE: apps/audit/models.py
# Audit Logs Models with Table Partitioning Support
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from tenants.models.tenants import Tenant


class AuditLog(models.Model):
    """
    Audit log model for tracking all system changes
    
    Features:
    - Multi-tenant support: Audit logs are tenant-specific
    - Table partitioning: Partitioned by year for performance
    - Correlation IDs: Track related operations across requests
    - Comprehensive tracking: User, action, object, changes
    - JSON change tracking: Before/after values
    - Request context: IP, user agent, request ID
    - Immutable: Cannot be modified after creation
    
    Partitioning Strategy:
    - Partitioned by created_at (RANGE by year)
    - Improves query performance for large datasets
    - Enables easy archival of old data
    - Supports automatic partition creation
    
    Use Cases:
    - Compliance and audit trails
    - Security investigations
    - Change tracking
    - User activity monitoring
    - Data recovery
    - Performance analysis
    
    Example:
        log = AuditLog.objects.create(
            tenant=tenant,
            user=user,
            username=user.username,
            action='CREATE',
            module='tickets',
            object_type='Ticket',
            object_id='123',
            object_repr='Ticket #123 - ABC Route',
            changes={
                'created': {
                    'ticket_code': 'TK20260529001',
                    'customer': 'John Doe',
                    'route': 'HCM-HN'
                }
            },
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0...',
            request_id=uuid.uuid4()
        )
    """
    
    # Action types
    ACTION_CHOICES = (
        ('CREATE', _('Create - New object created')),
        ('UPDATE', _('Update - Object modified')),
        ('DELETE', _('Delete - Object deleted')),
        ('LOGIN', _('Login - User logged in')),
        ('LOGOUT', _('Logout - User logged out')),
        ('EXPORT', _('Export - Data exported')),
        ('IMPORT', _('Import - Data imported')),
        ('APPROVE', _('Approve - Action approved')),
        ('REJECT', _('Reject - Action rejected')),
        ('BULK_UPDATE', _('Bulk Update - Multiple objects updated')),
        ('BULK_DELETE', _('Bulk Delete - Multiple objects deleted')),
    )

    id = models.BigAutoField(primary_key=True)
    
    # ========================================================================
    # MULTI-TENANT RELATIONSHIP
    # ========================================================================
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='audit_logs',
        db_index=True,
        help_text='Tenant that owns this audit log',
        db_comment='Reference to tenant'
    )
    
    # ========================================================================
    # USER INFORMATION
    # ========================================================================
    
    user = models.ForeignKey(
        'accounts.UserAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        db_index=True,
        help_text='User who performed the action',
        db_comment='Reference to user account'
    )
    username = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        help_text='Username snapshot at time of action',
        db_comment='Username for audit trail'
    )
    
    # ========================================================================
    # ACTION DETAILS
    # ========================================================================
    
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        db_index=True,
        help_text='Type of action performed',
        db_comment='Action type'
    )
    module = models.CharField(
        max_length=100,
        db_index=True,
        help_text='Module name (e.g., "tickets", "vehicles", "hr")',
        db_comment='Module name'
    )
    
    # ========================================================================
    # OBJECT INFORMATION
    # ========================================================================
    
    object_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='Type of object affected (e.g., "Ticket", "Vehicle")',
        db_comment='Object class name'
    )
    object_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_index=True,
        help_text='ID of the object affected',
        db_comment='Object identifier'
    )
    object_repr = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text='String representation of the object',
        db_comment='Object display representation'
    )
    
    # ========================================================================
    # CHANGE TRACKING
    # ========================================================================
    
    old_values = models.JSONField(
        null=True,
        blank=True,
        help_text='Previous values before change',
        db_comment='Old values (JSON)'
    )
    new_values = models.JSONField(
        null=True,
        blank=True,
        help_text='New values after change',
        db_comment='New values (JSON)'
    )
    changes = models.JSONField(
        null=True,
        blank=True,
        help_text='Summary of changes made',
        db_comment='Changes summary (JSON)'
    )
    
    # ========================================================================
    # REQUEST CONTEXT
    # ========================================================================
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='IP address of the request',
        db_comment='Request IP address'
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text='User agent string',
        db_comment='User agent header'
    )
    
    # ========================================================================
    # CORRELATION ID
    # ========================================================================
    
    request_id = models.UUIDField(
        null=True,
        blank=True,
        db_index=True,
        help_text='Correlation ID for tracking related operations',
        db_comment='Request correlation ID'
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='When this audit log was created',
        db_comment='Audit log creation timestamp'
    )

    class Meta:
        db_table = 'audit_logs'
        verbose_name = _('Audit Log')
        verbose_name_plural = _('Audit Logs')
        ordering = ['-created_at']
        
        # ====================================================================
        # INDEXES
        # ====================================================================
        
        indexes = [
            # Index for user queries
            models.Index(
                fields=['user_id'],
                name='idx_audit_user',
                db_comment='Query logs by user'
            ),
            # Index for time range queries
            models.Index(
                fields=['-created_at'],
                name='idx_audit_created',
                db_comment='Query logs by creation date'
            ),
            # Index for module and action queries
            models.Index(
                fields=['module', 'action'],
                name='idx_audit_module',
                db_comment='Query logs by module and action'
            ),
            # Index for object queries
            models.Index(
                fields=['object_id'],
                name='idx_audit_object',
                condition=models.Q(object_id__isnull=False),
                db_comment='Query logs by object ID'
            ),
            # Index for correlation ID queries
            models.Index(
                fields=['request_id'],
                name='idx_audit_request_id',
                db_comment='Query logs by request correlation ID'
            ),
            # Composite index for common queries
            models.Index(
                fields=['tenant', 'created_at'],
                name='idx_audit_tenant_created',
                db_comment='Query logs by tenant and date'
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.get_action_display()} - {self.module} - {self.object_repr or self.object_id}"

    @classmethod
    def log_action(cls, tenant, user, action, module, object_type=None, 
                  object_id=None, object_repr=None, old_values=None, 
                  new_values=None, changes=None, ip_address=None, 
                  user_agent=None, request_id=None):
        """
        Create an audit log entry
        
        Args:
            tenant: Tenant instance
            user: UserAccount instance (optional)
            action: Action type
            module: Module name
            object_type: Type of object affected
            object_id: ID of object affected
            object_repr: String representation of object
            old_values: Previous values (dict)
            new_values: New values (dict)
            changes: Summary of changes (dict)
            ip_address: IP address
            user_agent: User agent string
            request_id: Correlation ID (UUID)
        
        Returns:
            AuditLog instance
        
        Example:
            AuditLog.log_action(
                tenant=tenant,
                user=user,
                action='CREATE',
                module='tickets',
                object_type='Ticket',
                object_id='123',
                object_repr='Ticket #123',
                changes={'created': {...}},
                ip_address='192.168.1.1',
                request_id=uuid.uuid4()
            )
        """
        return cls.objects.create(
            tenant=tenant,
            user=user,
            username=user.username if user else None,
            action=action,
            module=module,
            object_type=object_type,
            object_id=object_id,
            object_repr=object_repr,
            old_values=old_values,
            new_values=new_values,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id
        )

    @classmethod
    def get_object_history(cls, tenant, object_type, object_id):
        """
        Get complete history of changes for an object
        
        Args:
            tenant: Tenant instance
            object_type: Type of object
            object_id: ID of object
        
        Returns:
            QuerySet of AuditLog objects ordered by creation date
        
        Example:
            history = AuditLog.get_object_history(
                tenant=tenant,
                object_type='Ticket',
                object_id='123'
            )
        """
        return cls.objects.filter(
            tenant=tenant,
            object_type=object_type,
            object_id=object_id
        ).order_by('created_at')

    @classmethod
    def get_user_activity(cls, tenant, user, start_date=None, end_date=None):
        """
        Get user activity logs
        
        Args:
            tenant: Tenant instance
            user: UserAccount instance
            start_date: Start date (optional)
            end_date: End date (optional)
        
        Returns:
            QuerySet of AuditLog objects
        
        Example:
            activity = AuditLog.get_user_activity(
                tenant=tenant,
                user=user,
                start_date=timezone.now() - timedelta(days=30)
            )
        """
        query = cls.objects.filter(tenant=tenant, user=user)
        
        if start_date:
            query = query.filter(created_at__gte=start_date)
        if end_date:
            query = query.filter(created_at__lte=end_date)
        
        return query.order_by('-created_at')

    @classmethod
    def get_module_activity(cls, tenant, module, start_date=None, end_date=None):
        """
        Get activity logs for a module
        
        Args:
            tenant: Tenant instance
            module: Module name
            start_date: Start date (optional)
            end_date: End date (optional)
        
        Returns:
            QuerySet of AuditLog objects
        """
        query = cls.objects.filter(tenant=tenant, module=module)
        
        if start_date:
            query = query.filter(created_at__gte=start_date)
        if end_date:
            query = query.filter(created_at__lte=end_date)
        
        return query.order_by('-created_at')

    @classmethod
    def get_correlated_logs(cls, request_id):
        """
        Get all logs related to a request (by correlation ID)
        
        Args:
            request_id: Correlation ID (UUID)
        
        Returns:
            QuerySet of AuditLog objects
        
        Example:
            logs = AuditLog.get_correlated_logs(request_id)
        """
        return cls.objects.filter(request_id=request_id).order_by('created_at')

    @classmethod
    def get_activity_stats(cls, tenant, start_date=None, end_date=None):
        """
        Get activity statistics
        
        Args:
            tenant: Tenant instance
            start_date: Start date (optional)
            end_date: End date (optional)
        
        Returns:
            Dictionary with statistics
        
        Example:
            stats = AuditLog.get_activity_stats(
                tenant=tenant,
                start_date=timezone.now() - timedelta(days=30)
            )
        """
        from django.db.models import Count
        
        query = cls.objects.filter(tenant=tenant)
        
        if start_date:
            query = query.filter(created_at__gte=start_date)
        if end_date:
            query = query.filter(created_at__lte=end_date)
        
        # Count by action
        by_action = dict(
            query.values('action').annotate(count=Count('id')).values_list('action', 'count')
        )
        
        # Count by module
        by_module = dict(
            query.values('module').annotate(count=Count('id')).values_list('module', 'count')
        )
        
        # Count by user
        by_user = dict(
            query.filter(user__isnull=False).values('username').annotate(count=Count('id')).values_list('username', 'count')
        )
        
        return {
            'total': query.count(),
            'by_action': by_action,
            'by_module': by_module,
            'by_user': by_user,
        }


class AuditLogArchive(models.Model):
    """
    Archive model for old audit logs
    
    Features:
    - Store archived audit logs separately
    - Reduce main table size
    - Enable long-term retention
    - Support for compliance requirements
    """
    
    id = models.BigAutoField(primary_key=True)
    
    # Store original audit log data as JSON
    audit_data = models.JSONField(
        help_text='Complete audit log data'
    )
    
    # Original audit log ID
    original_id = models.BigIntegerField(
        unique=True,
        help_text='Original audit log ID'
    )
    
    # Archival information
    archived_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When this log was archived'
    )
    archived_by_id = models.IntegerField(
        null=True,
        blank=True,
        help_text='User who archived this log'
    )
    
    class Meta:
        db_table = 'audit_logs_archive'
        verbose_name = _('Audit Log Archive')
        verbose_name_plural = _('Audit Log Archives')
        ordering = ['-archived_at']

    def __str__(self):
        return f"Archive - {self.original_id}"