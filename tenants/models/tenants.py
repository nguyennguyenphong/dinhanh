# ============================================================================
# FILE: apps/core/models.py
# Multi-Tenant Models
# ============================================================================

from django.db import models
from django.core.validators import URLValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
import uuid
from django.utils import timezone

class Tenant(models.Model):
    """
    Multi-tenant model for the Bus CMS system
    Each tenant is an independent bus company.
    """
    PLAN_CHOICES = (
        ('TRIAL', _('Trial')),
        ('STANDARD', _('Standard')),
        ('PROFESSIONAL', _('Professional')),
        ('ENTERPRISE', _('Enterprise')),
    )

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True
    )
    code = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9_]+$',
                message='Code chỉ chứa chữ hoa, số và dấu gạch dưới'
            )
        ],
        help_text='Mã định danh tenant (VD: DINHANH, VEXPRESS)'
    )
    name = models.CharField(
        max_length=255,
        help_text='Tên công ty nhà xe'
    )
    domain = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
        validators=[URLValidator()],
        help_text='Domain tùy chỉnh nếu là SaaS'
    )
    logo_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        help_text='URL logo công ty'
    )
    primary_color = models.CharField(
        max_length=7,
        default='#3B82F6',
        validators=[
            RegexValidator(
                regex=r'^#[0-9A-Fa-f]{6}$',
                message='Màu phải ở định dạng hex (#RRGGBB)'
            )
        ],
        help_text='Màu chính của giao diện'
    )
    plan = models.CharField(
        max_length=30,
        choices=PLAN_CHOICES,
        default='STANDARD',
        db_index=True,
        help_text='Gói dịch vụ'
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text='Tenant có hoạt động không'
    )
    
    # Tenant settings - JSON lưu trữ cấu hình override
    settings = models.JSONField(
        default=dict,
        blank=True,
        help_text='Cấu hình override cấp tenant'
    )
    
    # Subscription info
    subscription_started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Ngày bắt đầu gói dịch vụ'
    )
    subscription_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Ngày hết hạn gói dịch vụ'
    )
    
    # Limits
    max_users = models.IntegerField(
        default=10,
        help_text='Số lượng user tối đa'
    )
    max_branches = models.IntegerField(
        default=1,
        help_text='Số lượng chi nhánh tối đa'
    )
    max_vehicles = models.IntegerField(
        default=50,
        help_text='Số lượng xe tối đa'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tenants'
        verbose_name = _('Tenant')
        verbose_name_plural = _('Tenants')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code', 'is_active']),
            models.Index(fields=['plan', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"

    def is_trial_expired(self):
        """Kiểm tra trial có hết hạn không"""
        if self.plan != 'TRIAL':
            return False
        if not self.subscription_expires_at:
            return True
        return timezone.now() > self.subscription_expires_at

    def is_subscription_active(self):
        """Kiểm tra subscription có hoạt động không"""
        if not self.subscription_expires_at:
            return True
        return timezone.now() <= self.subscription_expires_at

    def get_plan_features(self):
        """Lấy features theo gói dịch vụ"""
        features = {
            'TRIAL': {
                'duration_days': 30,
                'max_users': 3,
                'max_branches': 1,
                'max_vehicles': 10,
                'features': ['basic_ticketing', 'basic_reporting']
            },
            'STANDARD': {
                'max_users': 10,
                'max_branches': 1,
                'max_vehicles': 50,
                'features': ['ticketing', 'hr', 'basic_cargo', 'reporting']
            },
            'PROFESSIONAL': {
                'max_users': 50,
                'max_branches': 5,
                'max_vehicles': 200,
                'features': ['ticketing', 'hr', 'cargo', 'reporting', 'api']
            },
            'ENTERPRISE': {
                'max_users': 999,
                'max_branches': 999,
                'max_vehicles': 9999,
                'features': ['all']
            }
        }
        return features.get(self.plan, {})


class TenantAuditLog(models.Model):
    """
    Audit log cho mỗi tenant
    Ghi lại tất cả thay đổi dữ liệu
    """
    ACTION_CHOICES = (
        ('CREATE', _('Create')),
        ('UPDATE', _('Update')),
        ('DELETE', _('Delete')),
        ('LOGIN', _('Login')),
        ('EXPORT', _('Export')),
    )

    id = models.BigAutoField(primary_key=True)
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='audit_logs',
        db_index=True
    )
    user_id = models.IntegerField(null=True, blank=True)
    username = models.CharField(max_length=150, null=True, blank=True)
    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES,
        db_index=True
    )
    module = models.CharField(max_length=100, db_index=True)
    object_type = models.CharField(max_length=100, null=True, blank=True)
    object_id = models.CharField(max_length=50, null=True, blank=True)
    object_repr = models.CharField(max_length=500, null=True, blank=True)
    
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    changes = models.JSONField(null=True, blank=True)
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    
    status = models.CharField(
        max_length=20,
        default='SUCCESS',
        choices=[('SUCCESS', 'Success'), ('FAILED', 'Failed')]
    )
    error_message = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'tenant_audit_logs'
        verbose_name = _('Tenant Audit Log')
        verbose_name_plural = _('Tenant Audit Logs')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'created_at']),
            models.Index(fields=['module', 'action']),
        ]

    def __str__(self):
        return f"{self.tenant.code} - {self.action} - {self.module}"


class TenantFeatureFlag(models.Model):
    """
    Feature flags per tenant
    Bật/tắt tính năng cho từng tenant
    """
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='feature_flags'
    )
    code = models.CharField(
        max_length=100,
        db_index=True,
        help_text='Mã feature (VD: ADVANCED_REPORTING)'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    is_enabled = models.BooleanField(default=False)
    rollout_percentage = models.PositiveIntegerField(
        default=100,
        validators=[
            lambda x: x >= 0 and x <= 100
        ],
        help_text='Phần trăm rollout (0-100)'
    )
    config = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tenant_feature_flags'
        unique_together = ('tenant', 'code')
        verbose_name = _('Tenant Feature Flag')
        verbose_name_plural = _('Tenant Feature Flags')

    def __str__(self):
        return f"{self.tenant.code} - {self.code}"


class TenantInvitation(models.Model):
    """
    Undangan untuk user tham gia tenant
    """
    STATUS_CHOICES = (
        ('PENDING', _('Pending')),
        ('ACCEPTED', _('Accepted')),
        ('REJECTED', _('Rejected')),
        ('EXPIRED', _('Expired')),
    )

    id = models.AutoField(primary_key=True)
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='invitations'
    )
    email = models.EmailField()
    token = models.CharField(max_length=255, unique=True, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    invited_by_id = models.IntegerField()
    
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tenant_invitations'
        verbose_name = _('Tenant Invitation')
        verbose_name_plural = _('Tenant Invitations')

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.tenant.code} - {self.email}"