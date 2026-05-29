# ============================================================================
# FILE: apps/core/models.py
# System Configuration Models with Encryption
# ============================================================================

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.conf import settings
from cryptography.fernet import Fernet
import json
from tenants.models.tenants import Tenant


class SystemConfig(models.Model):
    """
    System configuration model for managing application settings
    
    Features:
    - Multi-tenant support: Each tenant has own configurations
    - Encryption support: Encrypt sensitive values (API keys, passwords)
    - Type support: String, integer, boolean, JSON, secret, text
    - Environment awareness: Different configs for dev/staging/production
    - Caching: Cache configs for performance
    - Audit trail: Track who changed configs
    - Access control: Public/private configs
    - Read-only mode: Lock configs in production
    
    Categories:
    - GENERAL: General application settings
    - PAYMENT: Payment gateway configurations
    - SMS: SMS provider settings
    - EMAIL: Email provider settings
    - BOOKING: Booking system settings
    - PRINTING: Printing configurations
    - NOTIFICATION: Notification settings
    - SECURITY: Security settings
    - INTEGRATION: Third-party integrations
    - CUSTOM: Custom tenant settings
    
    Value Types:
    - string: Simple text value
    - integer: Integer number
    - boolean: True/False value
    - json: JSON object/array
    - secret: Encrypted sensitive value
    - text: Multi-line text
    
    Environment:
    - ALL: Available in all environments
    - DEVELOPMENT: Development only
    - STAGING: Staging only
    - PRODUCTION: Production only
    
    Example:
        config = SystemConfig.objects.create(
            tenant=tenant,
            category='PAYMENT',
            key='stripe_secret_key',
            value='sk_live_...',
            value_type='secret',
            label='Stripe Secret Key',
            description='Secret key for Stripe payment gateway',
            is_encrypted=True,
            is_public=False,
            is_readonly=True,
            env='PRODUCTION',
            updated_by=admin_user
        )
    """
    
    CATEGORY_CHOICES = (
        ('GENERAL', _('General - General application settings')),
        ('PAYMENT', _('Payment - Payment gateway configurations')),
        ('SMS', _('SMS - SMS provider settings')),
        ('EMAIL', _('Email - Email provider settings')),
        ('BOOKING', _('Booking - Booking system settings')),
        ('PRINTING', _('Printing - Printing configurations')),
        ('NOTIFICATION', _('Notification - Notification settings')),
        ('SECURITY', _('Security - Security settings')),
        ('INTEGRATION', _('Integration - Third-party integrations')),
        ('CUSTOM', _('Custom - Custom tenant settings')),
    )
    
    VALUE_TYPE_CHOICES = (
        ('string', _('String - Simple text value')),
        ('integer', _('Integer - Integer number')),
        ('boolean', _('Boolean - True/False value')),
        ('json', _('JSON - JSON object/array')),
        ('secret', _('Secret - Encrypted sensitive value')),
        ('text', _('Text - Multi-line text')),
    )
    
    ENV_CHOICES = (
        ('ALL', _('All - Available in all environments')),
        ('DEVELOPMENT', _('Development - Development only')),
        ('STAGING', _('Staging - Staging only')),
        ('PRODUCTION', _('Production - Production only')),
    )

    id = models.AutoField(primary_key=True)
    
    # ========================================================================
    # MULTI-TENANT RELATIONSHIP
    # ========================================================================
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='system_configs',
        db_index=True,
        help_text='Tenant that owns this configuration',
        db_comment='Reference to tenant'
    )
    
    # ========================================================================
    # CONFIGURATION IDENTIFICATION
    # ========================================================================
    
    category = models.CharField(
        max_length=60,
        choices=CATEGORY_CHOICES,
        db_index=True,
        help_text='Configuration category',
        db_comment='Config category'
    )
    key = models.CharField(
        max_length=120,
        validators=[
            RegexValidator(
                regex=r'^[a-z0-9_]+$',
                message='Key must contain only lowercase letters, numbers, and underscores'
            )
        ],
        help_text='Configuration key (e.g., "stripe_secret_key")',
        db_comment='Config key identifier'
    )
    
    # ========================================================================
    # CONFIGURATION VALUE
    # ========================================================================
    
    value = models.TextField(
        blank=True,
        null=True,
        help_text='Configuration value (encrypted if is_encrypted=True)',
        db_comment='Config value'
    )
    value_type = models.CharField(
        max_length=20,
        choices=VALUE_TYPE_CHOICES,
        default='string',
        help_text='Type of configuration value',
        db_comment='Value type'
    )
    
    # ========================================================================
    # METADATA
    # ========================================================================
    
    label = models.CharField(
        max_length=255,
        help_text='Human-readable label for the configuration',
        db_comment='Config label'
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Detailed description of what this config does',
        db_comment='Config description'
    )
    
    # ========================================================================
    # SECURITY & ACCESS CONTROL
    # ========================================================================
    
    is_encrypted = models.BooleanField(
        default=False,
        help_text='Value is encrypted (for sensitive data)',
        db_comment='Encryption flag'
    )
    is_public = models.BooleanField(
        default=False,
        help_text='Configuration is exposed to frontend',
        db_comment='Public flag'
    )
    is_readonly = models.BooleanField(
        default=False,
        help_text='Configuration is read-only (locked in production)',
        db_comment='Read-only flag'
    )
    
    # ========================================================================
    # ENVIRONMENT
    # ========================================================================
    
    env = models.CharField(
        max_length=20,
        choices=ENV_CHOICES,
        default='ALL',
        db_index=True,
        help_text='Environment where this config applies',
        db_comment='Environment'
    )
    
    # ========================================================================
    # AUDIT INFORMATION
    # ========================================================================
    
    updated_by = models.ForeignKey(
        'accounts.UserAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='config_updates',
        help_text='User who last updated this config',
        db_comment='Updated by user'
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='When this config was created',
        db_comment='Creation timestamp'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='When this config was last updated',
        db_comment='Last update timestamp'
    )

    class Meta:
        db_table = 'system_configs'
        verbose_name = _('System Config')
        verbose_name_plural = _('System Configs')
        ordering = ['category', 'key']
        
        # ====================================================================
        # CONSTRAINTS
        # ====================================================================
        
        constraints = [
            # Unique key per tenant and category
            models.UniqueConstraint(
                fields=['tenant', 'category', 'key'],
                name='unique_tenant_category_key',
                violation_error_message='Config key must be unique within tenant and category'
            ),
            # Validate value type
            models.CheckConstraint(
                check=models.Q(value_type__in=[
                    'string', 'integer', 'boolean', 'json', 'secret', 'text'
                ]),
                name='chk_config_type'
            ),
            # Validate environment
            models.CheckConstraint(
                check=models.Q(env__in=[
                    'ALL', 'DEVELOPMENT', 'STAGING', 'PRODUCTION'
                ]),
                name='chk_config_env'
            ),
        ]
        
        # ====================================================================
        # INDEXES
        # ====================================================================
        
        indexes = [
            # Index for finding configs by tenant and category
            models.Index(
                fields=['tenant', 'category'],
                name='idx_config_tenant_category',
                db_comment='Query configs by tenant and category'
            ),
            # Index for finding public configs
            models.Index(
                fields=['tenant', 'is_public'],
                name='idx_config_tenant_public',
                db_comment='Query public configs by tenant'
            ),
            # Index for environment queries
            models.Index(
                fields=['env'],
                name='idx_config_env',
                db_comment='Query configs by environment'
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.category} - {self.key} ({self.tenant.code})"

    def clean(self):
        """
        Validate configuration
        """
        # Validate value based on type
        if self.value_type == 'integer':
            try:
                int(self.value)
            except (ValueError, TypeError):
                raise ValidationError(
                    f'Value must be an integer for {self.key}'
                )
        
        elif self.value_type == 'boolean':
            if self.value not in ['true', 'false', 'True', 'False', '1', '0']:
                raise ValidationError(
                    f'Value must be boolean (true/false) for {self.key}'
                )
        
        elif self.value_type == 'json':
            try:
                json.loads(self.value)
            except (json.JSONDecodeError, TypeError):
                raise ValidationError(
                    f'Value must be valid JSON for {self.key}'
                )

    def save(self, *args, **kwargs):
        """Override save to enforce business rules"""
        self.clean()
        
        # Encrypt value if needed
        if self.is_encrypted and self.value:
            self.value = self._encrypt_value(self.value)
        
        # Clear cache when saving
        self._clear_cache()
        
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Override delete to clear cache"""
        self._clear_cache()
        super().delete(*args, **kwargs)

    # ========================================================================
    # ENCRYPTION METHODS
    # ========================================================================

    @staticmethod
    def _get_cipher():
        """Get Fernet cipher for encryption"""
        key = getattr(settings, 'CONFIG_ENCRYPTION_KEY', None)
        if not key:
            raise ValueError('CONFIG_ENCRYPTION_KEY not set in settings')
        return Fernet(key.encode() if isinstance(key, str) else key)

    def _encrypt_value(self, value):
        """
        Encrypt a value
        
        Args:
            value: Value to encrypt
        
        Returns:
            Encrypted value string
        """
        if not value:
            return value
        
        try:
            cipher = self._get_cipher()
            encrypted = cipher.encrypt(value.encode())
            return encrypted.decode()
        except Exception as e:
            raise ValidationError(f'Failed to encrypt value: {str(e)}')

    def _decrypt_value(self, value):
        """
        Decrypt a value
        
        Args:
            value: Encrypted value string
        
        Returns:
            Decrypted value
        """
        if not value or not self.is_encrypted:
            return value
        
        try:
            cipher = self._get_cipher()
            decrypted = cipher.decrypt(value.encode())
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f'Failed to decrypt value: {str(e)}')

    # ========================================================================
    # VALUE CONVERSION METHODS
    # ========================================================================

    def get_value(self):
        """
        Get configuration value with type conversion
        
        Returns:
            Value converted to appropriate type
        
        Example:
            value = config.get_value()
            # Returns: 'string', 123, True, {...}, etc.
        """
        # Decrypt if needed
        value = self._decrypt_value(self.value)
        
        if not value:
            return None
        
        # Convert based on type
        if self.value_type == 'integer':
            return int(value)
        
        elif self.value_type == 'boolean':
            return value.lower() in ['true', '1', 'yes']
        
        elif self.value_type == 'json':
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        
        else:  # string, text, secret
            return value

    def set_value(self, value):
        """
        Set configuration value
        
        Args:
            value: Value to set
        
        Example:
            config.set_value('new_value')
            config.save()
        """
        if isinstance(value, (dict, list)):
            self.value = json.dumps(value)
            self.value_type = 'json'
        elif isinstance(value, bool):
            self.value = 'true' if value else 'false'
            self.value_type = 'boolean'
        elif isinstance(value, int):
            self.value = str(value)
            self.value_type = 'integer'
        else:
            self.value = str(value)

    # ========================================================================
    # CACHE METHODS
    # ========================================================================

    def _get_cache_key(self):
        """Get cache key for this config"""
        return f"config_{self.tenant_id}_{self.category}_{self.key}"

    def _clear_cache(self):
        """Clear cache for this config"""
        cache.delete(self._get_cache_key())
        # Also clear tenant config cache
        cache.delete(f"config_{self.tenant_id}_all")

    def _get_from_cache(self):
        """Get value from cache"""
        return cache.get(self._get_cache_key())

    def _set_cache(self, value, timeout=3600):
        """Set value in cache"""
        cache.set(self._get_cache_key(), value, timeout)

    # ========================================================================
    # QUERY METHODS
    # ========================================================================

    @classmethod
    def get_config(cls, tenant, category, key, use_cache=True):
        """
        Get configuration value
        
        Args:
            tenant: Tenant instance
            category: Config category
            key: Config key
            use_cache: Use cache if available
        
        Returns:
            SystemConfig instance or None
        
        Example:
            config = SystemConfig.get_config(tenant, 'PAYMENT', 'stripe_key')
        """
        try:
            config = cls.objects.get(
                tenant=tenant,
                category=category,
                key=key
            )
            return config
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_value(cls, tenant, category, key, default=None, use_cache=True):
        """
        Get configuration value directly
        
        Args:
            tenant: Tenant instance
            category: Config category
            key: Config key
            default: Default value if not found
            use_cache: Use cache if available
        
        Returns:
            Configuration value or default
        
        Example:
            stripe_key = SystemConfig.get_value(
                tenant, 'PAYMENT', 'stripe_key'
            )
        """
        config = cls.get_config(tenant, category, key)
        if not config:
            return default
        
        return config.get_value() or default

    @classmethod
    def get_by_category(cls, tenant, category):
        """
        Get all configs in a category
        
        Args:
            tenant: Tenant instance
            category: Config category
        
        Returns:
            QuerySet of SystemConfig objects
        """
        return cls.objects.filter(
            tenant=tenant,
            category=category
        ).order_by('key')

    @classmethod
    def get_public_configs(cls, tenant):
        """
        Get all public configs (exposed to frontend)
        
        Args:
            tenant: Tenant instance
        
        Returns:
            Dictionary of public configs
        
        Example:
            public = SystemConfig.get_public_configs(tenant)
            # Returns: {'key1': 'value1', 'key2': 'value2', ...}
        """
        configs = cls.objects.filter(
            tenant=tenant,
            is_public=True
        )
        
        result = {}
        for config in configs:
            result[f"{config.category}_{config.key}"] = config.get_value()
        
        return result

    @classmethod
    def set_config(cls, tenant, category, key, value, updated_by=None, **kwargs):
        """
        Set or create configuration
        
        Args:
            tenant: Tenant instance
            category: Config category
            key: Config key
            value: Configuration value
            updated_by: User who updated
            **kwargs: Additional fields
        
        Returns:
            SystemConfig instance
        
        Example:
            config = SystemConfig.set_config(
                tenant=tenant,
                category='PAYMENT',
                key='stripe_key',
                value='sk_live_...',
                updated_by=admin_user,
                is_encrypted=True
            )
        """
        config, created = cls.objects.get_or_create(
            tenant=tenant,
            category=category,
            key=key,
            defaults={
                'value': value,
                'updated_by': updated_by,
                **kwargs
            }
        )
        
        if not created:
            config.value = value
            config.updated_by = updated_by
            for key, val in kwargs.items():
                setattr(config, key, val)
            config.save()
        
        return config


class SystemConfigAuditLog(models.Model):
    """
    Audit log for system configuration changes
    
    Features:
    - Track all config changes
    - Record who made changes and when
    - Store old and new values
    - Support for compliance audits
    """
    
    ACTION_CHOICES = (
        ('CREATE', _('Create - Config created')),
        ('UPDATE', _('Update - Config modified')),
        ('DELETE', _('Delete - Config deleted')),
    )

    id = models.BigAutoField(primary_key=True)
    
    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================
    
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='config_audit_logs',
        db_index=True,
        help_text='Tenant that owns this audit log'
    )
    
    config = models.ForeignKey(
        SystemConfig,
        on_delete=models.CASCADE,
        related_name='audit_logs',
        null=True,
        blank=True,
        help_text='Config affected by this change'
    )
    
    # ========================================================================
    # ACTION DETAILS
    # ========================================================================
    
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        db_index=True,
        help_text='Type of action performed'
    )
    
    actor = models.ForeignKey(
        'accounts.UserAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='config_actions_performed',
        help_text='User who performed the action'
    )
    
    # ========================================================================
    # CHANGE DETAILS
    # ========================================================================
    
    old_value = models.TextField(
        blank=True,
        null=True,
        help_text='Previous value (masked if sensitive)'
    )
    new_value = models.TextField(
        blank=True,
        null=True,
        help_text='New value (masked if sensitive)'
    )
    
    reason = models.TextField(
        blank=True,
        null=True,
        help_text='Reason for the change'
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'system_config_audit_logs'
        verbose_name = _('System Config Audit Log')
        verbose_name_plural = _('System Config Audit Logs')
        ordering = ['-created_at']
        
        indexes = [
            models.Index(
                fields=['tenant', 'created_at'],
                name='idx_config_audit_tenant_created'
            ),
            models.Index(
                fields=['config', 'created_at'],
                name='idx_config_audit_config_created'
            ),
        ]

    def __str__(self):
        return f"{self.action} - {self.config.key if self.config else 'N/A'}"

    @classmethod
    def log_action(cls, tenant, config, action, actor=None,
                  old_value=None, new_value=None, reason=None):
        """
        Log a config action
        
        Args:
            tenant: Tenant instance
            config: SystemConfig instance
            action: Action type
            actor: UserAccount instance
            old_value: Previous value (masked if sensitive)
            new_value: New value (masked if sensitive)
            reason: Reason for action
        
        Returns:
            SystemConfigAuditLog instance
        """
        return cls.objects.create(
            tenant=tenant,
            config=config,
            action=action,
            actor=actor,
            old_value=old_value,
            new_value=new_value,
            reason=reason
        )