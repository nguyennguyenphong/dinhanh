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
        help_text='Tenant that owns this configuration'
    )
    
    # ========================================================================
    # CONFIGURATION IDENTIFICATION
    # ========================================================================
    
    category = models.CharField(
        max_length=60,
        choices=CATEGORY_CHOICES,
        db_index=True,
        help_text='Configuration category'
    )
    key = models.CharField(
        max_length=120,
        validators=[
            RegexValidator(
                regex=r'^[a-z0-9_]+$',
                message='Key must contain only lowercase letters, numbers, and underscores'
            )
        ],
        help_text='Configuration key (e.g., "stripe_secret_key")'
    )
    
    # ========================================================================
    # CONFIGURATION VALUE
    # ========================================================================
    
    value = models.TextField(
        blank=True,
        null=True,
        help_text='Configuration value (encrypted if is_encrypted=True)'
    )
    value_type = models.CharField(
        max_length=20,
        choices=VALUE_TYPE_CHOICES,
        default='string',
        help_text='Type of configuration value'
    )
    
    # ========================================================================
    # METADATA
    # ========================================================================
    
    label = models.CharField(
        max_length=255,
        help_text='Human-readable label for the configuration'
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Detailed description of what this config does'
    )
    
    # ========================================================================
    # SECURITY & ACCESS CONTROL
    # ========================================================================
    
    is_encrypted = models.BooleanField(
        default=False,
        help_text='Value is encrypted (for sensitive data)'
    )
    is_public = models.BooleanField(
        default=False,
        help_text='Configuration is exposed to frontend'
    )
    is_readonly = models.BooleanField(
        default=False,
        help_text='Configuration is read-only (locked in production)'
    )
    
    # ========================================================================
    # ENVIRONMENT
    # ========================================================================
    
    env = models.CharField(
        max_length=20,
        choices=ENV_CHOICES,
        default='ALL',
        db_index=True,
        help_text='Environment where this config applies'
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
        help_text='User who last updated this config'
    )
    
    # ========================================================================
    # TIMESTAMPS
    # ========================================================================
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='When this config was created'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='When this config was last updated'
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
            models.UniqueConstraint(
                fields=['tenant', 'category', 'key'],
                name='unique_tenant_category_key',
                violation_error_message='Config key must be unique within tenant and category'
            ),
            models.CheckConstraint(
                condition=models.Q(
                    value_type__in=[
                        'string', 'integer', 'boolean', 'json', 'secret', 'text'
                    ]
                ),
                name='chk_config_type'
            ),

            models.CheckConstraint(
                condition=models.Q(
                    env__in=[
                        'ALL', 'DEVELOPMENT', 'STAGING', 'PRODUCTION'
                    ]
                ),
                name='chk_config_env'
            ),
        ]
        
        # ====================================================================
        # INDEXES
        # ====================================================================
        
        indexes = [
            models.Index(
                fields=['tenant', 'category'],
                name='idx_config_tenant_category'
            ),
            models.Index(
                fields=['tenant', 'is_public'],
                name='idx_config_tenant_public'
            ),
            models.Index(
                fields=['env'],
                name='idx_config_env'
            ),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.category} - {self.key} ({self.tenant.code})"

    def clean(self):
        """Validate configuration"""
        if self.value_type == 'integer':
            try:
                int(self.value)
            except (ValueError, TypeError):
                raise ValidationError(f'Value must be an integer for {self.key}')
        elif self.value_type == 'boolean':
            if self.value not in ['true', 'false', 'True', 'False', '1', '0']:
                raise ValidationError(f'Value must be boolean (true/false) for {self.key}')
        elif self.value_type == 'json':
            try:
                json.loads(self.value)
            except (json.JSONDecodeError, TypeError):
                raise ValidationError(f'Value must be valid JSON for {self.key}')

    def save(self, *args, **kwargs):
        """Override save to enforce business rules"""
        self.clean()
        if self.is_encrypted and self.value:
            self.value = self._encrypt_value(self.value)
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
        if not value: return value
        try:
            cipher = self._get_cipher()
            return cipher.encrypt(value.encode()).decode()
        except Exception as e:
            raise ValidationError(f'Failed to encrypt value: {str(e)}')

    def _decrypt_value(self, value):
        if not value or not self.is_encrypted: return value
        try:
            cipher = self._get_cipher()
            return cipher.decrypt(value.encode()).decode()
        except Exception as e:
            raise ValueError(f'Failed to decrypt value: {str(e)}')

    # ========================================================================
    # VALUE CONVERSION & CACHE METHODS
    # ========================================================================

    def get_value(self):
        value = self._decrypt_value(self.value)
        if not value: return None
        if self.value_type == 'integer': return int(value)
        if self.value_type == 'boolean': return value.lower() in ['true', '1', 'yes']
        if self.value_type == 'json':
            try: return json.loads(value)
            except json.JSONDecodeError: return None
        return value

    def set_value(self, value):
        if isinstance(value, (dict, list)):
            self.value = json.dumps(value); self.value_type = 'json'
        elif isinstance(value, bool):
            self.value = 'true' if value else 'false'; self.value_type = 'boolean'
        elif isinstance(value, int):
            self.value = str(value); self.value_type = 'integer'
        else: self.value = str(value)

    def _get_cache_key(self): return f"config_{self.tenant_id}_{self.category}_{self.key}"
    def _clear_cache(self):
        cache.delete(self._get_cache_key())
        cache.delete(f"config_{self.tenant_id}_all")

    # ========================================================================
    # QUERY METHODS
    # ========================================================================

    @classmethod
    def get_config(cls, tenant, category, key, use_cache=True):
        try: return cls.objects.get(tenant=tenant, category=category, key=key)
        except cls.DoesNotExist: return None

    @classmethod
    def get_value(cls, tenant, category, key, default=None, use_cache=True):
        config = cls.get_config(tenant, category, key)
        return config.get_value() or default if config else default

    @classmethod
    def get_public_configs(cls, tenant):
        configs = cls.objects.filter(tenant=tenant, is_public=True)
        return {f"{c.category}_{c.key}": c.get_value() for c in configs}

    @classmethod
    def set_config(cls, tenant, category, key, value, updated_by=None, **kwargs):
        config, created = cls.objects.get_or_create(
            tenant=tenant, category=category, key=key,
            defaults={'value': value, 'updated_by': updated_by, **kwargs}
        )
        if not created:
            config.value = value; config.updated_by = updated_by
            for k, v in kwargs.items(): setattr(config, k, v)
            config.save()
        return config


class SystemConfigAuditLog(models.Model):
    ACTION_CHOICES = (
        ('CREATE', _('Create - Config created')),
        ('UPDATE', _('Update - Config modified')),
        ('DELETE', _('Delete - Config deleted')),
    )

    id = models.BigAutoField(primary_key=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='config_audit_logs', db_index=True)
    config = models.ForeignKey(SystemConfig, on_delete=models.CASCADE, related_name='system_config_audit_logs', null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, db_index=True)
    actor = models.ForeignKey('accounts.UserAccount', on_delete=models.SET_NULL, null=True, blank=True, related_name='config_actions_performed')
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'system_config_audit_logs'
        verbose_name = _('System Config Audit Log')
        verbose_name_plural = _('System Config Audit Logs')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'created_at'], name='idx_config_audit_tenant_created'),
            models.Index(fields=['config', 'created_at'], name='idx_config_audit_config_created'),
        ]

    def __str__(self):
        return f"{self.action} - {self.config.key if self.config else 'N/A'}"