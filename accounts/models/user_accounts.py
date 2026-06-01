# ============================================================================
# FILE: apps/accounts/models.py
# User Account Models with Security Features
# ============================================================================

import base64
import uuid
from io import BytesIO

import pyotp
import qrcode
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from tenants.models.tenants import Tenant


class UserAccountManager(BaseUserManager):
    """
    Custom user manager for multi-tenant user creation

    Features:
    - Create users with tenant isolation
    - Validate email and username uniqueness per tenant
    - Hash passwords securely
    - Support for superuser creation
    """

    def create_user(self, tenant, username, email, password=None, **extra_fields):
        """
        Create and save a regular user

        Args:
            tenant: Tenant instance
            username: Unique username per tenant
            email: Unique email per tenant
            password: User password
            **extra_fields: Additional fields

        Returns:
            UserAccount instance

        Raises:
            ValueError: If required fields are missing
        """
        if not tenant:
            raise ValueError("Tenant must be provided")
        if not username:
            raise ValueError("Username must be provided")
        if not email:
            raise ValueError("Email must be provided")

        # Normalize email
        email = self.normalize_email(email)

        # Check uniqueness per tenant
        if UserAccount.objects.filter(tenant=tenant, username=username).exists():
            raise ValueError(f'Username "{username}" already exists in this tenant')
        if UserAccount.objects.filter(tenant=tenant, email=email).exists():
            raise ValueError(f'Email "{email}" already exists in this tenant')

        # Create user
        user = self.model(tenant=tenant, username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, tenant, username, email, password=None, **extra_fields):
        """
        Create and save a superuser

        Args:
            tenant: Tenant instance
            username: Unique username
            email: Unique email
            password: User password
            **extra_fields: Additional fields

        Returns:
            UserAccount instance
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(tenant, username, email, password, **extra_fields)


class UserAccount(AbstractBaseUser):
    """
    Custom user account model with multi-tenant support and security features

    Features:
    - Multi-tenant isolation: Each tenant has isolated users
    - UUID for external API references
    - Two-factor authentication (2FA) support
    - Account locking after failed login attempts
    - Password expiration and change tracking
    - Login history (IP, timestamp)
    - User preferences (JSON)
    - Soft delete support via is_active flag
    - Comprehensive audit trail

    Security Features:
    - Password hashing (PBKDF2 by default)
    - 2FA with TOTP (Time-based One-Time Password)
    - Account lockout after N failed attempts
    - Failed login tracking
    - Last login IP tracking
    - Password change enforcement

    Example:
        user = UserAccount.objects.create_user(
            tenant=tenant,
            username='john.doe',
            email='john@example.com',
            password='secure_password',
            full_name='John Doe',
            phone='+84912345678'
        )
    """

    # ========================================================================
    # IDENTIFICATION
    # ========================================================================

    id = models.AutoField(primary_key=True)

    # UUID for external API references
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        help_text="Unique identifier for external API calls",
    )

    # ========================================================================
    # MULTI-TENANT RELATIONSHIP
    # ========================================================================

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="user_accounts",
        db_index=True,
        help_text="Tenant that owns this user",
    )

    # ========================================================================
    # AUTHENTICATION FIELDS
    # ========================================================================

    username = models.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r"^[a-zA-Z0-9._-]+$",
                message="Username can only contain letters, numbers, dots, underscores, and hyphens",
            )
        ],
        help_text="Unique username per tenant",
    )
    email = models.EmailField(
        max_length=254,
        validators=[EmailValidator()],
        help_text="Unique email per tenant",
    )
    password = models.CharField(max_length=255, help_text="Hashed password (PBKDF2)")

    # ========================================================================
    # PROFILE INFORMATION
    # ========================================================================

    full_name = models.CharField(max_length=255, help_text="User full name")
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$", message="Invalid phone number format"
            )
        ],
        help_text="User phone number",
    )
    avatar = models.URLField(
        max_length=500, blank=True, null=True, help_text="URL to user avatar image"
    )

    # ========================================================================
    # ORGANIZATIONAL RELATIONSHIP
    # ========================================================================

    branch = models.ForeignKey(
        "branches.Branch",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
        help_text="Branch where user works",
    )

    # ========================================================================
    # STATUS FLAGS
    # ========================================================================

    is_active = models.BooleanField(
        default=True, db_index=True, help_text="User account is active"
    )
    is_staff = models.BooleanField(
        default=False, help_text="User can access admin interface"
    )
    is_superuser = models.BooleanField(
        default=False, help_text="User has all permissions"
    )

    # ========================================================================
    # PASSWORD MANAGEMENT
    # ========================================================================

    must_change_password = models.BooleanField(
        default=False, help_text="User must change password on next login"
    )
    last_password_change = models.DateTimeField(
        null=True, blank=True, help_text="When password was last changed"
    )
    password_expires_at = models.DateTimeField(
        null=True, blank=True, help_text="When password expires (null = never)"
    )

    # ========================================================================
    # TWO-FACTOR AUTHENTICATION (2FA)
    # ========================================================================

    two_fa_enabled = models.BooleanField(
        default=False, help_text="Two-factor authentication is enabled"
    )
    two_fa_secret = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="TOTP secret for 2FA (encrypted in production)",
    )
    two_fa_backup_codes = models.JSONField(
        default=list, blank=True, help_text="Backup codes for 2FA recovery"
    )

    # ========================================================================
    # LOGIN TRACKING
    # ========================================================================

    last_login = models.DateTimeField(
        null=True, blank=True, help_text="Last successful login timestamp"
    )
    last_login_ip = models.GenericIPAddressField(
        null=True, blank=True, help_text="IP address of last login"
    )

    # ========================================================================
    # SECURITY - FAILED LOGIN TRACKING
    # ========================================================================

    failed_login_count = models.SmallIntegerField(
        default=0, help_text="Number of consecutive failed login attempts"
    )
    locked_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Account locked until this time (null = not locked)",
    )

    # ========================================================================
    # USER PREFERENCES
    # ========================================================================

    preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text="User UI preferences (theme, language, etc.)",
    )

    # ========================================================================
    # TIMESTAMPS
    # ========================================================================

    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True, help_text="When user account was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="When user account was last updated"
    )

    # Set custom user manager
    objects = UserAccountManager()

    # Required for AbstractBaseUser
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "full_name"]

    class Meta:
        db_table = "user_accounts"
        verbose_name = _("User Account")
        verbose_name_plural = _("User Accounts")
        ordering = ["-created_at"]

        # ====================================================================
        # CONSTRAINTS
        # ====================================================================

        constraints = [
            # Unique username per tenant
            models.UniqueConstraint(
                fields=["tenant", "username"],
                name="unique_tenant_username",
                violation_error_message="Username already exists in this tenant",
            ),
            # Unique email per tenant
            models.UniqueConstraint(
                fields=["tenant", "email"],
                name="unique_tenant_email",
                violation_error_message="Email already exists in this tenant",
            ),
        ]

        # ====================================================================
        # INDEXES
        # ====================================================================

        indexes = [
            # Index for finding active users
            models.Index(fields=["tenant", "is_active"], name="idx_user_tenant_active"),
            # Index for email lookups
            models.Index(fields=["tenant", "email"], name="idx_user_tenant_email"),
            # Index for username lookups
            models.Index(
                fields=["tenant", "username"], name="idx_user_tenant_username"
            ),
            # Index for locked accounts
            models.Index(fields=["locked_until"], name="idx_user_locked_until"),
            # Index for staff users
            models.Index(fields=["is_staff"], name="idx_user_is_staff"),
        ]

    def __str__(self):
        """String representation"""
        return f"{self.full_name} ({self.username}) - {self.tenant.code}"

    def save(self, *args, **kwargs):
        """
        Override save to enforce business rules
        """
        # Normalize email
        self.email = self.normalize_email(self.email)

        # Validate tenant consistency
        if self.branch and self.branch.tenant_id != self.tenant_id:
            raise ValidationError("Branch must belong to the same tenant")

        super().save(*args, **kwargs)

    # ========================================================================
    # AUTHENTICATION METHODS
    # ========================================================================

    def check_password(self, raw_password):
        """
        Check if provided password matches the stored hash

        Args:
            raw_password: Plain text password to check

        Returns:
            Boolean
        """
        return super().check_password(raw_password)

    def set_password(self, raw_password):
        """
        Hash and set password

        Args:
            raw_password: Plain text password
        """
        super().set_password(raw_password)
        self.last_password_change = timezone.now()

    # ========================================================================
    # ACCOUNT LOCKING METHODS
    # ========================================================================

    def is_locked(self):
        """
        Check if account is currently locked

        Returns:
            Boolean
        """
        if not self.locked_until:
            return False

        if timezone.now() > self.locked_until:
            # Lock has expired, unlock account
            self.unlock_account()
            return False

        return True

    def lock_account(self, duration_minutes=30):
        """
        Lock account for specified duration

        Args:
            duration_minutes: How long to lock (default 30 minutes)

        Example:
            user.lock_account(duration_minutes=15)
        """
        self.locked_until = timezone.now() + timezone.timedelta(
            minutes=duration_minutes
        )
        self.save(update_fields=["locked_until"])

    def unlock_account(self):
        """
        Unlock account and reset failed login counter
        """
        self.locked_until = None
        self.failed_login_count = 0
        self.save(update_fields=["locked_until", "failed_login_count"])

    def increment_failed_login(self):
        """
        Increment failed login counter and lock if threshold exceeded

        Locks account if MAX_LOGIN_ATTEMPTS exceeded
        """
        from django.conf import settings

        max_attempts = getattr(settings, "MAX_LOGIN_ATTEMPTS", 5)
        lockout_duration = getattr(settings, "LOCKOUT_DURATION_MINUTES", 30)

        self.failed_login_count += 1

        if self.failed_login_count >= max_attempts:
            self.lock_account(duration_minutes=lockout_duration)
        else:
            self.save(update_fields=["failed_login_count"])

    def reset_failed_login(self):
        """
        Reset failed login counter after successful login
        """
        self.failed_login_count = 0
        self.save(update_fields=["failed_login_count"])

    # ========================================================================
    # TWO-FACTOR AUTHENTICATION METHODS
    # ========================================================================

    def setup_2fa(self):
        """
        Setup two-factor authentication

        Returns:
            Dictionary with secret and QR code

        Example:
            setup = user.setup_2fa()
            # Returns: {
            #     'secret': 'JBSWY3DPEBLW64TMMQ',
            #     'qr_code': 'data:image/png;base64,...'
            # }
        """
        # Generate secret
        secret = pyotp.random_base32()

        # Create provisioning URI for QR code
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=self.email, issuer_name=self.tenant.name
        )

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr_code = base64.b64encode(buffer.getvalue()).decode()

        return {
            "secret": secret,
            "qr_code": f"data:image/png;base64,{qr_code}",
            "provisioning_uri": provisioning_uri,
        }

    def enable_2fa(self, secret, token):
        """
        Enable 2FA after verifying token

        Args:
            secret: TOTP secret from setup_2fa()
            token: 6-digit code from authenticator app

        Returns:
            Boolean (True if successful)

        Raises:
            ValidationError if token is invalid
        """
        totp = pyotp.TOTP(secret)

        # Verify token (allow 30 second window)
        if not totp.verify(token, valid_window=1):
            raise ValidationError("Invalid 2FA token")

        # Generate backup codes
        backup_codes = [pyotp.random_base32()[:8] for _ in range(10)]

        # Save 2FA settings
        self.two_fa_secret = secret
        self.two_fa_enabled = True
        self.two_fa_backup_codes = backup_codes
        self.save(
            update_fields=["two_fa_secret", "two_fa_enabled", "two_fa_backup_codes"]
        )

        return True

    def disable_2fa(self):
        """
        Disable two-factor authentication
        """
        self.two_fa_secret = None
        self.two_fa_enabled = False
        self.two_fa_backup_codes = []
        self.save(
            update_fields=["two_fa_secret", "two_fa_enabled", "two_fa_backup_codes"]
        )

    def verify_2fa_token(self, token):
        """
        Verify 2FA token during login

        Args:
            token: 6-digit code from authenticator app

        Returns:
            Boolean
        """
        if not self.two_fa_enabled or not self.two_fa_secret:
            return False

        totp = pyotp.TOTP(self.two_fa_secret)
        return totp.verify(token, valid_window=1)

    def verify_2fa_backup_code(self, backup_code):
        """
        Verify 2FA backup code (one-time use)

        Args:
            backup_code: Backup code from setup

        Returns:
            Boolean
        """
        if backup_code not in self.two_fa_backup_codes:
            return False

        # Remove used backup code
        self.two_fa_backup_codes.remove(backup_code)
        self.save(update_fields=["two_fa_backup_codes"])

        return True

    # ========================================================================
    # LOGIN TRACKING METHODS
    # ========================================================================

    def record_login(self, ip_address=None):
        """
        Record successful login

        Args:
            ip_address: IP address of login

        Example:
            user.record_login(ip_address='192.168.1.1')
        """
        self.last_login = timezone.now()
        self.last_login_ip = ip_address
        self.failed_login_count = 0
        self.save(update_fields=["last_login", "last_login_ip", "failed_login_count"])

    # ========================================================================
    # PASSWORD MANAGEMENT METHODS
    # ========================================================================

    def is_password_expired(self):
        """
        Check if password has expired

        Returns:
            Boolean
        """
        if not self.password_expires_at:
            return False

        return timezone.now() > self.password_expires_at

    def require_password_change(self):
        """
        Force user to change password on next login
        """
        self.must_change_password = True
        self.save(update_fields=["must_change_password"])

    def change_password(self, raw_password):
        """
        Change user password

        Args:
            raw_password: New password

        Example:
            user.change_password('new_secure_password')
        """
        self.set_password(raw_password)
        self.must_change_password = False
        self.save(
            update_fields=["password", "last_password_change", "must_change_password"]
        )

    # ========================================================================
    # PERMISSION METHODS
    # ========================================================================

    def has_permission(self, permission_code):
        """
        Check if user has specific permission

        Args:
            permission_code: Permission code (e.g., 'tickets.view_ticket')

        Returns:
            Boolean
        """
        if self.is_superuser:
            return True

        from accounts.models.role_permissions import RolePermission

        return RolePermission.objects.filter(
            role__users__user=self, permission__codename=permission_code, is_active=True
        ).exists()

    def has_module_permission(self, module):
        """
        Check if user has any permission in module

        Args:
            module: Module name (e.g., 'tickets')

        Returns:
            Boolean
        """
        if self.is_superuser:
            return True

        from accounts.models.role_permissions import RolePermission

        return RolePermission.objects.filter(
            role__users__user=self, permission__module=module, is_active=True
        ).exists()

    def get_permissions(self):
        """
        Get all permissions for user

        Returns:
            QuerySet of Permission objects
        """
        if self.is_superuser:
            from accounts.models.permissions import Permission

            return Permission.objects.filter(tenant=self.tenant)

        from accounts.models.role_permissions import RolePermission

        return (
            RolePermission.objects.filter(role__users__user=self, is_active=True)
            .select_related("permission")
            .values_list("permission", flat=True)
        )

    # ========================================================================
    # PREFERENCE METHODS
    # ========================================================================

    def get_preference(self, key, default=None):
        """
        Get user preference value

        Args:
            key: Preference key
            default: Default value if not found

        Returns:
            Preference value

        Example:
            theme = user.get_preference('theme', 'light')
        """
        return self.preferences.get(key, default)

    def set_preference(self, key, value):
        """
        Set user preference value

        Args:
            key: Preference key
            value: Preference value

        Example:
            user.set_preference('theme', 'dark')
        """
        self.preferences[key] = value
        self.save(update_fields=["preferences"])

    def get_all_preferences(self):
        """
        Get all user preferences

        Returns:
            Dictionary of preferences
        """
        return self.preferences.copy()
