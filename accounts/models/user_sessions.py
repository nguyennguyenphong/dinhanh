# ============================================================================
# FILE: apps/accounts/models.py
# User Session Models with JWT Support
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
import json
from datetime import timedelta
import jwt
from django.conf import settings


class UserSession(models.Model):
    """
    User session model for tracking active sessions
    
    Features:
    - JWT-based authentication tokens
    - Refresh token support for token rotation
    - Device tracking and fingerprinting
    - IP address and user agent logging
    - Session expiration management
    - Soft delete via revocation timestamp
    - Multi-device session support
    - Session revocation and invalidation
    - Concurrent session management
    
    Security Features:
    - Unique session tokens
    - Token expiration
    - Refresh token rotation
    - Device fingerprinting
    - IP tracking for anomaly detection
    - Session revocation support
    - Automatic cleanup of expired sessions
    
    JWT Token Structure:
    {
        'user_id': int,
        'session_id': int,
        'tenant_id': int,
        'iat': timestamp,
        'exp': timestamp,
        'type': 'access'
    }
    
    Refresh Token Structure:
    {
        'user_id': int,
        'session_id': int,
        'tenant_id': int,
        'iat': timestamp,
        'exp': timestamp,
        'type': 'refresh'
    }
    
    Example:
        # Create session
        session = UserSession.objects.create(
            user=user,
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0...',
            device_info={'device': 'desktop', 'os': 'Windows'}
        )
        
        # Generate tokens
        tokens = session.generate_tokens()
        # Returns: {'access': 'eyJ...', 'refresh': 'eyJ...'}
        
        # Verify token
        user = UserSession.verify_token(tokens['access'])
        
        # Refresh token
        new_tokens = session.refresh_tokens()
        
        # Revoke session
        session.revoke()
    """
    
    id = models.BigAutoField(primary_key=True)
    
    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================
    
    user = models.ForeignKey(
        'UserAccount',
        on_delete=models.CASCADE,
        related_name='sessions',
        db_index=True,
        help_text='User who owns this session',
        db_comment='Reference to user account'
    )
    
    # ========================================================================
    # SESSION TOKENS
    # ========================================================================
    
    session_token = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text='JWT access token for API requests',
        db_comment='Access token (JWT)'
    )
    refresh_token = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text='JWT refresh token for obtaining new access tokens',
        db_comment='Refresh token (JWT)'
    )
    
    # ========================================================================
    # DEVICE INFORMATION
    # ========================================================================
    
    device_info = models.TextField(
        blank=True,
        null=True,
        help_text='Device information (JSON: device type, OS, browser, etc.)',
        db_comment='Device fingerprint data'
    )
    ip_address = models.GenericIPAddressField(
        help_text='IP address of the session',
        db_comment='Session IP address'
    )
    user_agent = models.TextField(
        help_text='User agent string (browser/device info)',
        db_comment='User agent header'
    )
    
    # ========================================================================
    # SESSION TIMING
    # ========================================================================
    
    expires_at = models.DateTimeField(
        db_index=True,
        help_text='When this session expires',
        db_comment='Session expiration timestamp'
    )
    last_activity = models.DateTimeField(
        auto_now=True,
        help_text='Last activity timestamp for this session',
        db_comment='Last activity timestamp'
    )
    
    # ========================================================================
    # REVOCATION
    # ========================================================================
    
    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text='When this session was revoked (null = active)',
        db_comment='Session revocation timestamp'
    )
    revocation_reason = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Reason for revocation (logout, security, etc.)',
        db_comment='Revocation reason'
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='When this session was created',
        db_comment='Session creation timestamp'
    )

    class Meta:
        db_table = 'user_sessions'
        verbose_name = _('User Session')
        verbose_name_plural = _('User Sessions')
        ordering = ['-created_at']
        
        # ====================================================================
        # INDEXES
        # ====================================================================
        
        indexes = [
            # Index for finding active sessions
            models.Index(
                fields=['user', 'revoked_at'],
                name='idx_session_user_active',
                db_comment='Query active sessions for a user'
            ),
            # Index for token lookups
            models.Index(
                fields=['session_token'],
                name='idx_session_token',
                db_comment='Query session by access token'
            ),
            # Index for refresh token lookups
            models.Index(
                fields=['refresh_token'],
                name='idx_session_refresh_token',
                db_comment='Query session by refresh token'
            ),
            # Index for expired sessions
            models.Index(
                fields=['expires_at'],
                name='idx_session_expires_at',
                db_comment='Query expired sessions'
            ),
            # Composite index for common queries
            models.Index(
                fields=['user', 'expires_at', 'revoked_at'],
                name='idx_session_composite',
                db_comment='Composite index for session queries'
            ),
        ]

    def __str__(self):
        """String representation"""
        status = 'revoked' if self.revoked_at else 'active'
        return f"{self.user.username} - {self.ip_address} ({status})"

    def is_active(self):
        """
        Check if session is currently active
        
        Returns:
            Boolean
        """
        # Check if revoked
        if self.revoked_at:
            return False
        
        # Check if expired
        if timezone.now() > self.expires_at:
            return False
        
        return True

    def is_expired(self):
        """
        Check if session has expired
        
        Returns:
            Boolean
        """
        return timezone.now() > self.expires_at

    def get_device_info(self):
        """
        Get parsed device information
        
        Returns:
            Dictionary with device info
        """
        if not self.device_info:
            return {}
        
        try:
            return json.loads(self.device_info)
        except json.JSONDecodeError:
            return {}

    def set_device_info(self, device_info):
        """
        Set device information
        
        Args:
            device_info: Dictionary with device info
        """
        self.device_info = json.dumps(device_info)

    # ========================================================================
    # TOKEN GENERATION
    # ========================================================================

    def generate_tokens(self):
        """
        Generate JWT access and refresh tokens
        
        Returns:
            Dictionary with access and refresh tokens
        
        Example:
            tokens = session.generate_tokens()
            # Returns: {
            #     'access': 'eyJ0eXAiOiJKV1QiLCJhbGc...',
            #     'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGc...',
            #     'expires_in': 3600
            # }
        """
        
        now = timezone.now()
        access_token_expires = now + timedelta(
            seconds=getattr(settings, 'JWT_ACCESS_TOKEN_LIFETIME', 3600)
        )
        refresh_token_expires = now + timedelta(
            seconds=getattr(settings, 'JWT_REFRESH_TOKEN_LIFETIME', 86400 * 7)
        )
        
        # Access token payload
        access_payload = {
            'user_id': self.user_id,
            'session_id': self.id,
            'tenant_id': self.user.tenant_id,
            'iat': int(now.timestamp()),
            'exp': int(access_token_expires.timestamp()),
            'type': 'access'
        }
        
        # Refresh token payload
        refresh_payload = {
            'user_id': self.user_id,
            'session_id': self.id,
            'tenant_id': self.user.tenant_id,
            'iat': int(now.timestamp()),
            'exp': int(refresh_token_expires.timestamp()),
            'type': 'refresh'
        }
        
        # Generate tokens
        access_token = jwt.encode(
            access_payload,
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        refresh_token = jwt.encode(
            refresh_payload,
            settings.SECRET_KEY,
            algorithm='HS256'
        )
        
        # Save tokens
        self.session_token = access_token
        self.refresh_token = refresh_token
        self.expires_at = access_token_expires
        self.save(update_fields=['session_token', 'refresh_token', 'expires_at'])
        
        return {
            'access': access_token,
            'refresh': refresh_token,
            'expires_in': getattr(settings, 'JWT_ACCESS_TOKEN_LIFETIME', 3600)
        }

    def refresh_tokens(self):
        """
        Generate new tokens using refresh token
        
        Returns:
            Dictionary with new access and refresh tokens
        
        Raises:
            ValidationError if session is invalid
        
        Example:
            new_tokens = session.refresh_tokens()
        """
        if not self.is_active():
            raise ValidationError('Session is not active')
        
        # Verify refresh token
        try:
            payload = jwt.decode(
                self.refresh_token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            
            if payload.get('type') != 'refresh':
                raise ValidationError('Invalid refresh token type')
        except jwt.ExpiredSignatureError:
            raise ValidationError('Refresh token has expired')
        except jwt.InvalidTokenError:
            raise ValidationError('Invalid refresh token')
        
        # Generate new tokens
        return self.generate_tokens()

    # ========================================================================
    # TOKEN VERIFICATION
    # ========================================================================

    @staticmethod
    def verify_token(token):
        """
        Verify JWT token and return user
        
        Args:
            token: JWT token string
        
        Returns:
            UserAccount instance or None
        
        Raises:
            ValidationError if token is invalid
        
        Example:
            user = UserSession.verify_token(token)
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            
            if payload.get('type') != 'access':
                raise ValidationError('Invalid token type')
            
            # Get session
            session = UserSession.objects.get(
                id=payload['session_id'],
                session_token=token
            )
            
            if not session.is_active():
                raise ValidationError('Session is not active')
            
            return session.user
        except jwt.ExpiredSignatureError:
            raise ValidationError('Token has expired')
        except jwt.InvalidTokenError:
            raise ValidationError('Invalid token')
        except UserSession.DoesNotExist:
            raise ValidationError('Session not found')

    @staticmethod
    def verify_refresh_token(token):
        """
        Verify refresh token and return session
        
        Args:
            token: Refresh token string
        
        Returns:
            UserSession instance
        
        Raises:
            ValidationError if token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            
            if payload.get('type') != 'refresh':
                raise ValidationError('Invalid token type')
            
            # Get session
            session = UserSession.objects.get(
                id=payload['session_id'],
                refresh_token=token
            )
            
            if not session.is_active():
                raise ValidationError('Session is not active')
            
            return session
        except jwt.ExpiredSignatureError:
            raise ValidationError('Refresh token has expired')
        except jwt.InvalidTokenError:
            raise ValidationError('Invalid refresh token')
        except UserSession.DoesNotExist:
            raise ValidationError('Session not found')

    # ========================================================================
    # SESSION MANAGEMENT
    # ========================================================================

    def revoke(self, reason='logout'):
        """
        Revoke this session (logout)
        
        Args:
            reason: Reason for revocation (logout, security, etc.)
        
        Example:
            session.revoke(reason='User logout')
        """
        self.revoked_at = timezone.now()
        self.revocation_reason = reason
        self.save(update_fields=['revoked_at', 'revocation_reason'])

    def update_activity(self):
        """
        Update last activity timestamp
        
        Called on each API request to track session activity
        """
        self.save(update_fields=['last_activity'])

    @classmethod
    def create_session(cls, user, ip_address, user_agent, device_info=None):
        """
        Create new user session
        
        Args:
            user: UserAccount instance
            ip_address: IP address of the session
            user_agent: User agent string
            device_info: Device information dictionary
        
        Returns:
            UserSession instance with generated tokens
        
        Example:
            session = UserSession.create_session(
                user=user,
                ip_address='192.168.1.1',
                user_agent='Mozilla/5.0...',
                device_info={'device': 'desktop', 'os': 'Windows'}
            )
            tokens = session.generate_tokens()
        """
        expires_at = timezone.now() + timedelta(
            seconds=getattr(settings, 'JWT_ACCESS_TOKEN_LIFETIME', 3600)
        )
        
        session = cls.objects.create(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=expires_at
        )
        
        if device_info:
            session.set_device_info(device_info)
            session.save(update_fields=['device_info'])
        
        return session

    @classmethod
    def get_active_sessions(cls, user):
        """
        Get all active sessions for a user
        
        Args:
            user: UserAccount instance
        
        Returns:
            QuerySet of active UserSession objects
        
        Example:
            sessions = UserSession.get_active_sessions(user)
        """
        now = timezone.now()
        return cls.objects.filter(
            user=user,
            revoked_at__isnull=True,
            expires_at__gt=now
        ).order_by('-created_at')

    @classmethod
    def revoke_all_sessions(cls, user, reason='security'):
        """
        Revoke all sessions for a user
        
        Args:
            user: UserAccount instance
            reason: Reason for revocation
        
        Example:
            UserSession.revoke_all_sessions(user, reason='Password changed')
        """
        sessions = cls.get_active_sessions(user)
        for session in sessions:
            session.revoke(reason=reason)

    @classmethod
    def cleanup_expired_sessions(cls):
        """
        Delete expired sessions (cleanup task)
        
        Should be called periodically via Celery task
        """
        now = timezone.now()
        expired_sessions = cls.objects.filter(
            expires_at__lt=now
        )
        count = expired_sessions.count()
        expired_sessions.delete()
        return count


class SessionAuditLog(models.Model):
    """
    Audit log for session events
    
    Features:
    - Track session creation, revocation, and suspicious activity
    - Record IP changes
    - Detect concurrent sessions from different locations
    - Support for security investigations
    
    Example:
        log = SessionAuditLog.objects.create(
            user=user,
            session=session,
            event_type='LOGIN',
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0...'
        )
    """
    
    EVENT_CHOICES = (
        ('LOGIN', _('Login - Session created')),
        ('LOGOUT', _('Logout - Session revoked')),
        ('TOKEN_REFRESH', _('Token Refresh - New tokens generated')),
        ('ACTIVITY', _('Activity - Session activity recorded')),
        ('SUSPICIOUS', _('Suspicious - Suspicious activity detected')),
        ('EXPIRED', _('Expired - Session expired')),
        ('REVOKED', _('Revoked - Session revoked for security')),
    )

    id = models.BigAutoField(primary_key=True)
    
    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================
    
    user = models.ForeignKey(
        'UserAccount',
        on_delete=models.CASCADE,
        related_name='session_audit_logs',
        db_index=True,
        help_text='User who owns the session'
    )
    session = models.ForeignKey(
        UserSession,
        on_delete=models.CASCADE,
        related_name='audit_logs',
        null=True,
        blank=True,
        help_text='Session related to this event'
    )
    
    # ========================================================================
    # EVENT DETAILS
    # ========================================================================
    
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_CHOICES,
        db_index=True,
        help_text='Type of session event'
    )
    ip_address = models.GenericIPAddressField(
        help_text='IP address of the event'
    )
    user_agent = models.TextField(
        help_text='User agent at time of event'
    )
    
    # ========================================================================
    # DETAILS
    # ========================================================================
    
    details = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional event details'
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'session_audit_logs'
        verbose_name = _('Session Audit Log')
        verbose_name_plural = _('Session Audit Logs')
        ordering = ['-created_at']
        
        indexes = [
            models.Index(
                fields=['user', 'created_at'],
                name='idx_session_audit_user_created'
            ),
            models.Index(
                fields=['event_type'],
                name='idx_session_audit_event_type'
            ),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_event_type_display()}"

    @classmethod
    def log_event(cls, user, session, event_type, ip_address, user_agent, details=None):
        """
        Log session event
        
        Args:
            user: UserAccount instance
            session: UserSession instance (optional)
            event_type: Type of event
            ip_address: IP address
            user_agent: User agent string
            details: Additional details
        
        Returns:
            SessionAuditLog instance
        """
        return cls.objects.create(
            user=user,
            session=session,
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {}
        )