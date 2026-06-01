# ============================================================================
# FILE: apps/features/models.py
# Feature Flags Models with A/B Testing Support
# ============================================================================

import hashlib

from django.contrib.postgres.fields import ArrayField
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from tenants.models.tenants import Tenant


class FeatureFlag(models.Model):
    """
    Feature flag model for controlling feature rollout and A/B testing

    Features:
    - Multi-tenant support: Each tenant has own feature flags
    - Rollout percentage: Gradual rollout with A/B testing support
    - Role-based access: Enable features for specific roles
    - User whitelisting: Enable features for specific users
    - Time-based activation: Valid from/to dates
    - Metadata storage: Store additional configuration
    - Caching: Cache flag status for performance
    - Audit trail: Track flag changes

    Use Cases:
    - Gradual feature rollout (0-100%)
    - A/B testing (50% users get feature A, 50% get feature B)
    - Beta features (enable for specific roles)
    - Feature gates (enable/disable features)
    - Canary deployments (enable for small % first)
    - Time-limited features (valid from/to dates)

    Rollout Strategy:
    - 0%: Feature disabled for all users
    - 1-99%: Feature enabled for X% of users (hash-based)
    - 100%: Feature enabled for all users

    Access Control:
    - If allowed_roles: User must have one of the roles
    - If allowed_users: User must be in the whitelist
    - If neither: Feature available to all (subject to rollout %)

    Example:
        flag = FeatureFlag.objects.create(
            tenant=tenant,
            key='online_payment_vnpay',
            label='VNPay Online Payment',
            description='Enable VNPay payment gateway',
            is_enabled=True,
            rollout_pct=50,  # 50% users
            allowed_roles=[manager_role.id],
            valid_from=timezone.now(),
            valid_to=timezone.now() + timedelta(days=30)
        )

        # Check if user has access
        if FeatureFlag.is_enabled_for_user(flag, user):
            # Show feature
    """

    id = models.AutoField(primary_key=True)

    # ========================================================================
    # MULTI-TENANT RELATIONSHIP
    # ========================================================================

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="feature_flags",
        db_index=True,
        help_text="Tenant that owns this feature flag",
    )

    # ========================================================================
    # IDENTIFICATION
    # ========================================================================

    key = models.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                regex=r"^[a-z0-9_]+$",
                message="Key must contain only lowercase letters, numbers, and underscores",
            )
        ],
        help_text='Unique key for the feature flag (e.g., "online_payment_vnpay")',
    )
    label = models.CharField(
        max_length=255, help_text="Human-readable label for the feature"
    )
    description = models.TextField(
        blank=True, null=True, help_text="Detailed description of the feature"
    )

    # ========================================================================
    # STATUS & ROLLOUT
    # ========================================================================

    is_enabled = models.BooleanField(
        default=False, db_index=True, help_text="Feature flag is enabled"
    )
    rollout_pct = models.SmallIntegerField(
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentage of users to enable feature for (0-100)",
    )

    # ========================================================================
    # ACCESS CONTROL
    # ========================================================================

    allowed_roles = ArrayField(
        models.IntegerField(),
        null=True,
        blank=True,
        help_text="List of role IDs that can access this feature (null = all roles)",
    )
    allowed_users = ArrayField(
        models.IntegerField(),
        null=True,
        blank=True,
        help_text="List of user IDs that can access this feature (whitelist)",
    )

    # ========================================================================
    # TIME-BASED ACTIVATION
    # ========================================================================

    valid_from = models.DateTimeField(
        null=True, blank=True, help_text="Feature becomes active from this date"
    )
    valid_to = models.DateTimeField(
        null=True, blank=True, help_text="Feature becomes inactive after this date"
    )

    # ========================================================================
    # METADATA
    # ========================================================================

    metadata = models.JSONField(
        default=dict, blank=True, help_text="Additional configuration and metadata"
    )

    # ========================================================================
    # TIMESTAMPS
    # ========================================================================

    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, help_text="When this feature flag was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="When this feature flag was last updated"
    )

    class Meta:
        db_table = "feature_flags"
        verbose_name = _("Feature Flag")
        verbose_name_plural = _("Feature Flags")
        ordering = ["key"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Unique key per tenant
            models.UniqueConstraint(
                fields=["tenant", "key"],
                name="unique_tenant_feature_key",
                violation_error_message="Feature key must be unique within tenant",
            ),
            # Validate rollout percentage
            models.CheckConstraint(
                condition=models.Q(rollout_pct__gte=0, rollout_pct__lte=100),
                name="chk_rollout_pct",
            ),
        ]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Index for finding enabled flags
            models.Index(
                fields=["tenant", "is_enabled"], name="idx_feature_tenant_enabled"
            ),
            # Index for time-based queries
            models.Index(
                fields=["valid_from", "valid_to"], name="idx_feature_valid_dates"
            ),
        ]

    def __str__(self):
        """String representation"""
        status = "✓" if self.is_enabled else "✗"
        return f"{status} {self.key} ({self.tenant.code})"

    def clean(self):
        """
        Validate feature flag
        """
        # Validate dates
        if self.valid_from and self.valid_to:
            if self.valid_from > self.valid_to:
                raise ValidationError("valid_from must be before valid_to")

    def save(self, *args, **kwargs):
        """Override save to enforce business rules"""
        self.clean()

        # Clear cache when saving
        self._clear_cache()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Override delete to clear cache"""
        self._clear_cache()
        super().delete(*args, **kwargs)

    # ========================================================================
    # CACHE METHODS
    # ========================================================================

    def _get_cache_key(self):
        """Get cache key for this flag"""
        return f"feature_flag_{self.tenant_id}_{self.key}"

    def _clear_cache(self):
        """Clear cache for this flag"""
        cache.delete(self._get_cache_key())
        # Also clear tenant flags cache
        cache.delete(f"feature_flags_{self.tenant_id}")

    # ========================================================================
    # STATUS METHODS
    # ========================================================================

    def is_active(self):
        """
        Check if feature flag is currently active

        Returns:
            Boolean
        """
        # Check if enabled
        if not self.is_enabled:
            return False

        # Check time-based activation
        now = timezone.now()

        if self.valid_from and now < self.valid_from:
            return False

        if self.valid_to and now > self.valid_to:
            return False

        return True

    def is_valid_for_user(self, user):
        """
        Check if feature is valid for a specific user

        Args:
            user: UserAccount instance

        Returns:
            Boolean

        Example:
            if flag.is_valid_for_user(user):
                # Feature is valid for this user
        """
        # Check if active
        if not self.is_active():
            return False

        # Check user whitelist
        if self.allowed_users and user.id not in self.allowed_users:
            return False

        # Check role restrictions
        if self.allowed_roles:
            user_roles = user.user_roles.filter(is_active=True).values_list(
                "role_id", flat=True
            )

            if not any(role_id in self.allowed_roles for role_id in user_roles):
                return False

        return True

    def is_enabled_for_user(self, user):
        """
        Check if feature is enabled for a specific user (includes rollout %)

        Args:
            user: UserAccount instance

        Returns:
            Boolean

        Example:
            if flag.is_enabled_for_user(user):
                # Show feature to user
        """
        # Check if valid for user
        if not self.is_valid_for_user(user):
            return False

        # If user is whitelisted, always enable
        if self.allowed_users and user.id in self.allowed_users:
            return True

        # Check rollout percentage
        if self.rollout_pct == 100:
            return True

        if self.rollout_pct == 0:
            return False

        # Hash-based rollout (consistent for same user)
        user_hash = int(
            hashlib.md5(f"{self.tenant_id}_{self.key}_{user.id}".encode()).hexdigest(),
            16,
        )

        return (user_hash % 100) < self.rollout_pct

    # ========================================================================
    # METADATA METHODS
    # ========================================================================

    def get_metadata(self, key, default=None):
        """
        Get metadata value

        Args:
            key: Metadata key
            default: Default value if not found

        Returns:
            Metadata value
        """
        return self.metadata.get(key, default)

    def set_metadata(self, key, value):
        """
        Set metadata value

        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value
        self.save(update_fields=["metadata"])

    # ========================================================================
    # QUERY METHODS
    # ========================================================================

    @classmethod
    def get_flag(cls, tenant, key):
        """
        Get feature flag by key

        Args:
            tenant: Tenant instance
            key: Feature flag key

        Returns:
            FeatureFlag instance or None

        Example:
            flag = FeatureFlag.get_flag(tenant, 'online_payment_vnpay')
        """
        try:
            return cls.objects.get(tenant=tenant, key=key)
        except cls.DoesNotExist:
            return None

    @classmethod
    def is_enabled(cls, tenant, key, user=None):
        """
        Check if feature is enabled

        Args:
            tenant: Tenant instance
            key: Feature flag key
            user: UserAccount instance (optional)

        Returns:
            Boolean

        Example:
            if FeatureFlag.is_enabled(tenant, 'online_payment_vnpay', user):
                # Show feature
        """
        flag = cls.get_flag(tenant, key)

        if not flag:
            return False

        if user:
            return flag.is_enabled_for_user(user)

        return flag.is_active()

    @classmethod
    def get_enabled_flags(cls, tenant, user=None):
        """
        Get all enabled feature flags

        Args:
            tenant: Tenant instance
            user: UserAccount instance (optional)

        Returns:
            QuerySet of FeatureFlag objects

        Example:
            flags = FeatureFlag.get_enabled_flags(tenant, user)
        """
        flags = cls.objects.filter(tenant=tenant, is_enabled=True)

        # Filter by time validity
        now = timezone.now()
        flags = flags.filter(
            models.Q(valid_from__isnull=True) | models.Q(valid_from__lte=now),
            models.Q(valid_to__isnull=True) | models.Q(valid_to__gte=now),
        )

        if user:
            # Filter by user access
            result = []
            for flag in flags:
                if flag.is_enabled_for_user(user):
                    result.append(flag)
            return result

        return flags

    @classmethod
    def get_flag_status(cls, tenant, user=None):
        """
        Get status of all flags for a user

        Args:
            tenant: Tenant instance
            user: UserAccount instance (optional)

        Returns:
            Dictionary with flag statuses

        Example:
            status = FeatureFlag.get_flag_status(tenant, user)
            # Returns: {
            #     'online_payment_vnpay': True,
            #     'new_dashboard': False,
            #     ...
            # }
        """
        flags = cls.objects.filter(tenant=tenant)

        result = {}
        for flag in flags:
            if user:
                result[flag.key] = flag.is_enabled_for_user(user)
            else:
                result[flag.key] = flag.is_active()

        return result


class FeatureFlagAuditLog(models.Model):
    """
    Audit log for feature flag changes

    Features:
    - Track all flag changes
    - Record who made changes and when
    - Support for compliance audits
    """

    ACTION_CHOICES = (
        ("CREATE", _("Create - Flag created")),
        ("UPDATE", _("Update - Flag modified")),
        ("DELETE", _("Delete - Flag deleted")),
        ("ENABLE", _("Enable - Flag enabled")),
        ("DISABLE", _("Disable - Flag disabled")),
    )

    id = models.BigAutoField(primary_key=True)

    # ========================================================================
    # RELATIONSHIPS
    # ========================================================================

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="feature_flag_audit_logs",
        db_index=True,
        help_text="Tenant that owns this audit log",
    )

    flag = models.ForeignKey(
        FeatureFlag,
        on_delete=models.CASCADE,
        related_name="feature_flag_audit_logs",
        help_text="Feature flag affected by this change",
    )

    # ========================================================================
    # ACTION DETAILS
    # ========================================================================

    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        db_index=True,
        help_text="Type of action performed",
    )

    actor = models.ForeignKey(
        "accounts.UserAccount",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="feature_flag_actions_performed",
        help_text="User who performed the action",
    )

    # ========================================================================
    # CHANGE DETAILS
    # ========================================================================

    old_values = models.JSONField(null=True, blank=True, help_text="Previous values")
    new_values = models.JSONField(null=True, blank=True, help_text="New values")

    reason = models.TextField(blank=True, null=True, help_text="Reason for the change")

    # ========================================================================
    # TIMESTAMPS
    # ========================================================================

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "feature_flag_audit_logs"
        verbose_name = _("Feature Flag Audit Log")
        verbose_name_plural = _("Feature Flag Audit Logs")
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=["tenant", "created_at"], name="idx_feature_audit_tenant_created"
            ),
            models.Index(
                fields=["flag", "created_at"], name="idx_feature_audit_flag_created"
            ),
        ]

    def __str__(self):
        return f"{self.action} - {self.flag.key}"

    @classmethod
    def log_action(
        cls,
        tenant,
        flag,
        action,
        actor=None,
        old_values=None,
        new_values=None,
        reason=None,
    ):
        """
        Log a feature flag action

        Args:
            tenant: Tenant instance
            flag: FeatureFlag instance
            action: Action type
            actor: UserAccount instance
            old_values: Previous values
            new_values: New values
            reason: Reason for action

        Returns:
            FeatureFlagAuditLog instance
        """
        return cls.objects.create(
            tenant=tenant,
            flag=flag,
            action=action,
            actor=actor,
            old_values=old_values,
            new_values=new_values,
            reason=reason,
        )
