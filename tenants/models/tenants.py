# ============================================================================
# FILE: tenants/models/tenants.py
# Multi-Tenant Models
# ============================================================================

import uuid

from django.core.validators import RegexValidator, URLValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from safedelete.models import SafeDeleteModel
from safedelete.models import SOFT_DELETE_CASCADE

from tenants.constants import (
    PLAN_ENTERPRISE,
    PLAN_PROFESSIONAL,
    PLAN_STANDARD,
    PLAN_TRIAL,
)


class Tenant(SafeDeleteModel):
    """
    Multi-tenant model for the Bus CMS system
    Each tenant is an independent bus company.
    """

    _safedelete_policy = SOFT_DELETE_CASCADE

    PLAN_CHOICES = (
        ("TRIAL", _("Trial")),
        ("STANDARD", _("Standard")),
        ("PROFESSIONAL", _("Professional")),
        ("ENTERPRISE", _("Enterprise")),
    )

    CURRENCY_CHOICES = (
        ("VND", _("Vietnam Dong (₫)")),
        ("USD", _("US Dollar ($)")),
        ("EUR", _("Euro (€)")),
        ("LAK", _("Lao Kip (₭)")),
        ("KHR", _("Cambodian Riel (៛)")),
    )

    LANGUAGE_CHOICES = (
        ("vi", _("Tiếng Việt")),
        ("en", _("English")),
        ("lo", _("Lao")),
        ("km", _("Khmer")),
    )

    TIMEZONE_CHOICES = (
        ("Asia/Ho_Chi_Minh", _("Asia/Ho_Chi_Minh (GMT+7)")),
        ("Asia/Vientiane", _("Asia/Vientiane (GMT+7)")),
        ("Asia/Phnom_Penh", _("Asia/Phnom_Penh (GMT+7)")),
        ("Asia/Bangkok", _("Asia/Bangkok (GMT+7)")),
    )

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, db_index=True
    )
    code = models.CharField(
        max_length=30,
        unique=True,
        db_index=True,
        validators=[
            RegexValidator(
                regex=r"^[A-Z0-9_]+$",
                message="Code chỉ chứa chữ hoa, số và dấu gạch dưới",
            )
        ],
        help_text="Mã định danh tenant (VD: DINHANH, VEXPRESS)",
    )
    name = models.CharField(max_length=255, help_text="Tên công ty nhà xe")
    domain = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
        validators=[URLValidator()],
        help_text="Domain tùy chỉnh nếu là SaaS",
    )
    logo_url = models.URLField(
        max_length=500, null=True, blank=True, help_text="URL logo công ty"
    )
    primary_color = models.CharField(
        max_length=7,
        default="#3B82F6",
        validators=[
            RegexValidator(
                regex=r"^#[0-9A-Fa-f]{6}$", message="Màu phải ở định dạng hex (#RRGGBB)"
            )
        ],
        help_text="Màu chính của giao diện",
    )
    plan = models.CharField(
        max_length=30,
        choices=PLAN_CHOICES,
        default=PLAN_STANDARD,
        db_index=True,
        help_text="Gói dịch vụ",
    )

    currency = models.CharField(
        max_length=10,
        choices=CURRENCY_CHOICES,
        default="VND",
        help_text="Đơn vị tiền tệ mặc định của nhà xe",
    )
    exchange_rate = models.DecimalField(
        max_length=10,
        max_digits=12,
        decimal_places=4,
        default=1.0000,
        help_text="Tỉ giá quy đổi so với đồng tiền gốc của hệ thống (VD: Hệ thống dùng USD, tỉ giá VND là 25000.0000)",
    )
    default_language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default="vi",
        help_text="Ngôn ngữ hiển thị mặc định cho backend/frontend của tenant",
    )
    timezone = models.CharField(
        max_length=50,
        choices=TIMEZONE_CHOICES,
        default="Asia/Ho_Chi_Minh",
        help_text="Múi giờ của nhà xe để đồng bộ thời gian chạy xe, lịch trình",
    )

    is_active = models.BooleanField(
        default=True, db_index=True, help_text="Tenant có hoạt động không"
    )

    # Tenant settings - JSON lưu trữ cấu hình override
    settings = models.JSONField(
        default=dict, blank=True, help_text="Cấu hình override cấp tenant"
    )

    # Subscription info
    subscription_started_at = models.DateTimeField(
        null=True, blank=True, help_text="Ngày bắt đầu gói dịch vụ"
    )
    subscription_expires_at = models.DateTimeField(
        null=True, blank=True, help_text="Ngày hết hạn gói dịch vụ"
    )

    # Limits
    max_users = models.IntegerField(default=10, help_text="Số lượng user tối đa")
    max_branches = models.IntegerField(default=1, help_text="Số lượng chi nhánh tối đa")
    max_vehicles = models.IntegerField(default=50, help_text="Số lượng xe tối đa")

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tenants"
        verbose_name = _("Tenant")
        verbose_name_plural = _("Tenants")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["code", "is_active"]),
            models.Index(fields=["plan", "is_active"]),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=['code'], 
                condition=models.Q(deleted__isnull=True), 
                name='unique_active_tenant_code'
            ),
            models.UniqueConstraint(
                fields=['domain'], 
                condition=models.Q(deleted__isnull=True), 
                name='unique_active_tenant_domain'
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"

    def is_trial_expired(self):
        """Kiểm tra trial có hết hạn không"""
        if self.plan != "TRIAL":
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
        from tenants.constants import PLAN_LIMITS

        return PLAN_LIMITS.get(self.plan, {})
