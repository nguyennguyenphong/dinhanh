# ============================================================================
# FILE: apps/api/models.py
# API Token Models with Security Features
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import ArrayField
import hashlib
import secrets
import string
from datetime import timedelta
from tenants.models.tenants import Tenant


class APIToken(models.Model):
    """
    API token model for secure API access
    
    Features:
    - Secure token generation: Random 32-character tokens
    - Token hashing: Store SHA256 hash, never store raw token
    - Token prefix: 8-character prefix for token identification
    - Scope-based access: Fine-grained permission control
    - Rate limiting: Per-token request rate limiting
    - Usage tracking: Track last used time and IP
    - Expiration: Optional token expiration
    - Branch isolation: Optional branch-specific tokens
    - Request counting: Track API usage
    - Audit trail: Track token creation and usage
    
    Token Format:
    - Generated: 32 random characters (a-z, 0-9)
    - Prefix: First 8 characters (used for identification)
    - Hash: SHA256 of full token (stored in DB)
    - Display: "prefix_****...****" (only prefix shown to user)
    
    Scopes:
    - bookings.read: Read booking data
    - bookings.write: Create/update bookings
    - bookings.delete: Delete bookings
    - trips.read: Read trip data
    - trips.write: Create/update trips
    - payments.read: Read payment data
    - payments.write: Process payments
    - users.read: Read user data
    - users.write: Manage users
    - admin: Full access
    
    Rate Limiting:
    - Per-token rate limit (default: 1000 requests/hour)
    - Tracked via request_count and reset hourly
    - Can be customized per token
    
    Example:
        # Create token
        token, token_string = APIToken.create_token(
            tenant=tenant,
            name='Mobile App',
            scopes=['bookings.read', 'trips.read'],
            created_by=user,
            rate_limit=5000
        )
        
        # Verify token
        token = APIToken.verify_token(token_string)
        
        # Check scope
        if token.has_scope('bookings.read'):
            # Allow access
        
        # Record usage
        token.record_usage(ip_address='192.168.1.1')
    """

    SCOPE_CHOICES = (
        ('bookings.read', _('Read bookings')),
        ('bookings.write', _('Create/update bookings')),
        ('bookings.delete', _('Delete bookings')),
        ('trips.read', _('Read trips')),
        ('trips.write', _('Create/update trips')),
        ('trips.delete', _('Delete trips')),
        ('payments.read', _('Read payments')),
        ('payments.write', _('Process payments')),
        ('users.read', _('Read users')),
        ('users.write', _('Manage users')),
        ('users.delete', _('Delete users')),
        ('admin', _('Full admin access')),
    )

    id = models.AutoField(primary_key=True)
    
    # ========================================================================
    # MULTI-TENANT RELATIONSHIP
    # ========================================================================
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='api_tokens',
        db_index=True,
        help_text='Tenant that owns this API token',
        db_comment='Reference to tenant'
    )
    
    # ========================================================================
    # TOKEN IDENTIFICATION
    # ========================================================================
    
    name = models.CharField(
        max_length=100,
        help_text='Human-readable name for the token (e.g., "Mobile App")',
        db_comment='Token name'
    )
    token_hash = models.CharField(
        max_length=255,
        unique=True,
        help_text='SHA256 hash of the token (never store raw token)',
        db_comment='Token hash'
    )
    token_prefix = models.CharField(
        max_length=8,
        db_index=True,
        help_text='First 8 characters of token for identification',
        db_comment='Token prefix'
    )
    
    # ========================================================================
    # PERMISSIONS & SCOPES
    # ========================================================================
    
    scopes = ArrayField(
        models.CharField(max_length=50),
        default=list,
        help_text='List of scopes this token has access to',
        db_comment='API scopes'
    )
    
    # ========================================================================
    # OWNERSHIP & BRANCH
    # ========================================================================
    
    created_by = models.ForeignKey(
        'accounts.UserAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='api_tokens_created',
        help_text='User who created this token',
        db_comment='Created by user'
    )
    branch_id = models.IntegerField(
        null=True,
        blank=True,
        help_text='Optional branch ID for branch-specific tokens',
        db_comment='Branch ID'
    )
    
    # ========================================================================
    # USAGE TRACKING
    # ========================================================================
    
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When this token was last used',
        db_comment='Last used timestamp'
    )
    last_used_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='IP address of last usage',
        db_comment='Last used IP'
    )
    request_count = models.BigIntegerField(
        default=0,
        help_text='Total number of requests made with this token',
        db_comment='Request count'
    )
    
    # ========================================================================
    # RATE LIMITING
    # ========================================================================
    
    rate_limit = models.IntegerField(
        default=1000,
        validators=[MinValueValidator(1)],
        help_text='Maximum requests per hour',
        db_comment='Rate limit (requests/hour)'
    )
    
    # ========================================================================
    # EXPIRATION & STATUS
    # ========================================================================
    
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Token expires at this date (null = no expiration)',
        db_comment='Expiration timestamp'
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text='Token is active and can be used',
        db_comment='Active status'
    )
    
    # ========================================================================
    # METADATA
    # ========================================================================
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text='Additional notes about this token',
        db_comment='Token notes'
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='When this token was created',
        db_comment='Creation timestamp'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='When this token was last updated',
        db_comment='Last update timestamp'
    )

    class Meta:
        db_table = 'api_tokens'
        verbose_name = _('API Token')
        verbose_name_plural = _('API Tokens')
        ordering = ['-created_at']
        
        # ====================================================================
        # INDEXES
        # ====================================================================
        
        indexes = [
            # Index for finding active tokens
            models.Index(
                fields=['is_active'],
                name='idx_api_tokens_active',
                db_comment='Query active tokens'
            ),
            # Index for token prefix lookup
            models.Index(
                fields=['token_prefix'],
                name='idx_api_tokens_prefix',
                db_comment='Query tokens by prefix'
            ),
            # Index for tenant and active
            models.Index(
                fields=['tenant', 'is_active'],
                name='idx_api_tokens_tenant_active',
                db_comment='Query active tokens by tenant'
            ),
            # Index for expiration queries
            models.Index(
                fields=['expires_at'],
                name='idx_api_tokens_expires',
                db_comment='Query expired tokens'
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.name} ({self.token_prefix}****)"

    def clean(self):
        """
        Validate API token
        """
        # Validate scopes
        valid_scopes = [scope[0] for scope in self.SCOPE_CHOICES]
        for scope in self.scopes:
            if scope not in valid_scopes:
                raise ValidationError(
                    f'Invalid scope: {scope}'
                )

    def save(self, *args, **kwargs):
        """Override save to enforce business rules"""
        self.clean()
        super().save(*args, **kwargs)

    # ========================================================================
    # TOKEN GENERATION & VERIFICATION
    # ========================================================================

    @staticmethod
    def _generate_token():
        """
        Generate a secure random token
        
        Returns:
            Tuple (token, prefix, hash)
        """
        # Generate 32-character random token
        alphabet = string.ascii_lowercase + string.digits
        token = ''.join(secrets.choice(alphabet) for _ in range(32))
        
        # Extract prefix (first 8 characters)
        prefix = token[:8]
        
        # Generate SHA256 hash
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        return token, prefix, token_hash

    @classmethod
    def create_token(cls, tenant, name, scopes, created_by=None,
                    branch_id=None, rate_limit=1000, expires_at=None,
                    notes=None):
        """
        Create a new API token
        
        Args:
            tenant: Tenant instance
            name: Token name
            scopes: List of scopes
            created_by: UserAccount instance
            branch_id: Optional branch ID
            rate_limit: Requests per hour
            expires_at: Optional expiration date
            notes: Optional notes
        
        Returns:
            Tuple (APIToken instance, token_string)
        
        Example:
            token, token_string = APIToken.create_token(
                tenant=tenant,
                name='Mobile App',
                scopes=['bookings.read', 'trips.read'],
                created_by=user,
                rate_limit=5000
            )
            # Return token_string to user (only shown once)
        """
        token, prefix, token_hash = cls._generate_token()
        
        api_token = cls.objects.create(
            tenant=tenant,
            name=name,
            token_hash=token_hash,
            token_prefix=prefix,
            scopes=scopes,
            created_by=created_by,
            branch_id=branch_id,
            rate_limit=rate_limit,
            expires_at=expires_at,
            notes=notes
        )
        
        return api_token, token

    @classmethod
    def verify_token(cls, token_string):
        """
        Verify and retrieve token
        
        Args:
            token_string: Raw token string
        
        Returns:
            APIToken instance or None
        
        Raises:
            ValueError: If token is invalid/expired
        
        Example:
            try:
                token = APIToken.verify_token(token_string)
            except ValueError as e:
                # Invalid or expired token
        """
        if not token_string or len(token_string) < 32:
            raise ValueError('Invalid token format')
        
        # Hash the token
        token_hash = hashlib.sha256(token_string.encode()).hexdigest()
        
        try:
            token = cls.objects.get(token_hash=token_hash)
        except cls.DoesNotExist:
            raise ValueError('Token not found')
        
        # Check if active
        if not token.is_active:
            raise ValueError('Token is inactive')
        
        # Check expiration
        if token.expires_at and timezone.now() > token.expires_at:
            raise ValueError('Token has expired')
        
        return token

    # ========================================================================
    # SCOPE METHODS
    # ========================================================================

    def has_scope(self, scope):
        """
        Check if token has a specific scope
        
        Args:
            scope: Scope to check
        
        Returns:
            Boolean
        
        Example:
            if token.has_scope('bookings.read'):
                # Allow access
        """
        # Admin scope has all permissions
        if 'admin' in self.scopes:
            return True
        
        return scope in self.scopes

    def has_scopes(self, scopes):
        """
        Check if token has all required scopes
        
        Args:
            scopes: List of scopes
        
        Returns:
            Boolean
        """
        return all(self.has_scope(scope) for scope in scopes)

    def has_any_scope(self, scopes):
        """
        Check if token has any of the required scopes
        
        Args:
            scopes: List of scopes
        
        Returns:
            Boolean
        """
        return any(self.has_scope(scope) for scope in scopes)

    # ========================================================================
    # USAGE TRACKING
    # ========================================================================

    def record_usage(self, ip_address=None):
        """
        Record token usage
        
        Args:
            ip_address: IP address of request
        
        Example:
            token.record_usage(ip_address='192.168.1.1')
        """
        self.last_used_at = timezone.now()
        if ip_address:
            self.last_used_ip = ip_address
        self.request_count += 1
        self.save(update_fields=['last_used_at', 'last_used_ip', 'request_count'])

    def get_usage_stats(self):
        """
        Get token usage statistics
        
        Returns:
            Dictionary with usage stats
        
        Example:
            stats = token.get_usage_stats()
            # Returns: {
            #     'total_requests': 1234,
            #     'last_used': '2026-05-29 23:58:00',
            #     'last_used_ip': '192.168.1.1',
            #     'created_days_ago': 30
            # }
        """
        created_days_ago = (timezone.now() - self.created_at).days
        
        return {
            'total_requests': self.request_count,
            'last_used': self.last_used_at.isoformat() if self.last_used_at else None,
            'last_used_ip': str(self.last_used_ip) if self.last_used_ip else None,
            'created_days_ago': created_days_ago,
            'avg_requests_per_day': self.request_count / max(created_days_ago, 1)
        }

    # ========================================================================
    # RATE LIMITING
    # ========================================================================

    def check_rate_limit(self):
        """
        Check if token has exceeded rate limit
        
        Returns:
            Boolean (True if within limit)
        
        Note:
            In production, use Redis for accurate rate limiting
        """
        # This is a simple implementation
        # For production, use Redis or similar
        # Reset request count hourly
        if self.last_used_at:
            time_since_last = timezone.now() - self.last_used_at
            if time_since_last > timedelta(hours=1):
                self.request_count = 0
                self.save(update_fields=['request_count'])
        
        return self.request_count < self.rate_limit

    # ========================================================================
    # STATUS METHODS
    # ========================================================================

    def is_valid(self):
        """
        Check if token is valid and usable
        
        Returns:
            Boolean
        """
        if not self.is_active:
            return False
        
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        
        return True

    def is_expired(self):
        """
        Check if token is expired
        
        Returns:
            Boolean
        """
        if not self.expires_at:
            return False
        
        return timezone.now() > self.expires_at

    # ========================================================================
    # QUERY METHODS
    # ========================================================================

    @classmethod
    def get_active_tokens(cls, tenant):
        """
        Get all active tokens for a tenant
        
        Args:
            tenant: Tenant instance
        
        Returns:
            QuerySet of APIToken objects
        """
        return cls.objects.filter(
            tenant=tenant,
            is_active=True
        ).filter(
            models.Q(expires_at__isnull=True) |
            models.Q(expires_at__gt=timezone.now())
        )

    @classmethod
    def get_expired_tokens(cls, tenant):
        """
        Get all expired tokens for a tenant
        
        Args:
            tenant: Tenant instance
        
        Returns:
            QuerySet of APIToken objects
        """
        return cls.objects.filter(
            tenant=tenant,
            expires_at__lt=timezone.now()
        )

    @classmethod
    def cleanup_expired_tokens(cls, days=90):
        """
        Delete expired tokens older than specified days
        
        Args:
            days: Delete tokens expired more than this many days ago
        
        Returns:
            Number of deleted tokens
        """
        cutoff_date = timezone.now() - timedelta(days=days)
        
        expired_tokens = cls.objects.filter(
            expires_at__lt=cutoff_date,
            is_active=False
        )
        count = expired_tokens.count()
        expired_tokens.delete()
        
        return count


class APITokenAuditLog(models.Model):
    """
    Audit log for API token access
    
    Features:
    - Track all API requests made with tokens
    - Record request details (method, endpoint, status)
    - Track rate limit violations
    - Security monitoring
    """
    
    ACTION_CHOICES = (
        ('CREATE', _('Create - Token created')),
        ('REVOKE', _('Revoke - Token revoked')),
        ('ACCESS', _('Access - Token used for API request')),
        ('RATE_LIMIT', _('Rate Limit - Rate limit exceeded')),
        ('SCOPE_DENIED', _('Scope Denied - Insufficient scope')),
    )

    id = models.BigAutoField(primary_key=True)
    
    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='api_token_audit_logs',
        db_index=True,
        help_text='Tenant that owns this audit log'
    )
    
    token = models.ForeignKey(
        APIToken,
        on_delete=models.CASCADE,
        related_name='audit_logs',
        help_text='API token used'
    )
    
    # ========================================================================
    # REQUEST DETAILS
    # ========================================================================
    
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        db_index=True,
        help_text='Type of action'
    )
    
    method = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text='HTTP method (GET, POST, etc.)'
    )
    
    endpoint = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='API endpoint accessed'
    )
    
    status_code = models.IntegerField(
        null=True,
        blank=True,
        help_text='HTTP response status code'
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='IP address of request'
    )
    
    user_agent = models.TextField(
        blank=True,
        null=True,
        help_text='User agent of request'
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'api_token_audit_logs'
        verbose_name = _('API Token Audit Log')
        verbose_name_plural = _('API Token Audit Logs')
        ordering = ['-created_at']
        
        indexes = [
            models.Index(
                fields=['token', 'created_at'],
                name='idx_api_audit_token_created'
            ),
            models.Index(
                fields=['action'],
                name='idx_api_audit_action'
            ),
        ]

    def __str__(self):
        return f"{self.action} - {self.token.name}"

    @classmethod
    def log_action(cls, tenant, token, action, method=None, endpoint=None,
                  status_code=None, ip_address=None, user_agent=None):
        """
        Log an API token action
        
        Args:
            tenant: Tenant instance
            token: APIToken instance
            action: Action type
            method: HTTP method
            endpoint: API endpoint
            status_code: HTTP status code
            ip_address: IP address
            user_agent: User agent
        
        Returns:
            APITokenAuditLog instance
        """
        return cls.objects.create(
            tenant=tenant,
            token=token,
            action=action,
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            ip_address=ip_address,
            user_agent=user_agent
        )