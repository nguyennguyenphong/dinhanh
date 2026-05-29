# ============================================================================
# FILE: apps/accounts/models.py
# Roles, Permissions, and User Account Models
# ============================================================================

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
import uuid
from tenants.models.tenants import Tenant


class Role(models.Model):
    """
    Role model for multi-tenant RBAC (Role-Based Access Control)
    
    Features:
    - Multi-tenant support: Each tenant has their own roles
    - System roles: Built-in roles that cannot be deleted
    - Slug-based identification: Unique identifier for each role
    - Soft delete support: Can be deactivated instead of deleted
    
    Example:
        Role.objects.create(
            tenant_id=1,
            name="Super Administrator",
            slug="super-admin",
            description="Full system access",
            is_system=True
        )
    """
    
    id = models.AutoField(primary_key=True)
    
    # Multi-tenant relationship
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='roles',
        db_index=True,
        help_text='Tenant that owns this role'
    )
    
    # Role identification
    name = models.CharField(
        max_length=100,
        help_text='Display name of the role (e.g., "Super Administrator")'
    )
    slug = models.CharField(
        max_length=100,
        validators=[
            RegexValidator(
                regex=r'^[a-z0-9-]+$',
                message='Slug must contain only lowercase letters, numbers, and hyphens'
            )
        ],
        help_text='Unique identifier for the role (e.g., "super-admin", "cashier")'
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Detailed description of role responsibilities'
    )
    
    # System flags
    is_system = models.BooleanField(
        default=False,
        help_text='System roles cannot be deleted and have predefined permissions'
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text='Inactive roles cannot be assigned to users'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'roles'
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')
        ordering = ['name']
        
        # Unique constraint: slug must be unique per tenant
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'slug'],
                name='unique_tenant_role_slug'
            ),
        ]
        
        # Indexes for common queries
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['is_system']),
        ]

    def __str__(self):
        return f"{self.name} ({self.tenant.code})"

    def save(self, *args, **kwargs):
        """
        Override save to auto-generate slug if not provided
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def can_be_deleted(self):
        """
        Check if role can be deleted
        System roles and roles with users cannot be deleted
        """
        if self.is_system:
            return False
        return not self.users.exists()

    def get_permissions(self):
        """
        Get all permissions assigned to this role
        Returns: QuerySet of Permission objects
        """
        return self.permissions.filter(is_active=True)

    def get_permission_codes(self):
        """
        Get list of permission codes for this role
        Useful for checking permissions in views
        Returns: List of permission codes (e.g., ['tickets.view', 'tickets.create'])
        """
        return list(self.permissions.filter(is_active=True).values_list('code', flat=True))


class Permission(models.Model):
    """
    Permission model for fine-grained access control
    
    Features:
    - Multi-tenant support: Permissions are tenant-specific
    - Module-based organization: Permissions grouped by module
    - Action-based naming: Standard CRUD operations
    - Hierarchical permissions: Can have parent permissions
    
    Permission Code Format: module.action
    Examples:
        - tickets.view
        - tickets.create
        - tickets.edit
        - tickets.delete
        - tickets.export
        - vehicles.view
        - vehicles.manage
    """
    
    ACTION_CHOICES = (
        ('view', _('View')),
        ('create', _('Create')),
        ('edit', _('Edit')),
        ('delete', _('Delete')),
        ('export', _('Export')),
        ('import', _('Import')),
        ('approve', _('Approve')),
        ('manage', _('Manage')),
    )

    id = models.AutoField(primary_key=True)
    
    # Multi-tenant relationship
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='permissions',
        db_index=True,
        help_text='Tenant that owns this permission'
    )
    
    # Permission identification
    code = models.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[a-z0-9._-]+$',
                message='Code must contain only lowercase letters, numbers, dots, underscores, and hyphens'
            )
        ],
        help_text='Unique permission code (e.g., "tickets.view", "vehicles.manage")'
    )
    name = models.CharField(
        max_length=255,
        help_text='Human-readable permission name'
    )
    
    # Organization
    module = models.CharField(
        max_length=100,
        db_index=True,
        help_text='Module name (e.g., "tickets", "vehicles", "hr")'
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        help_text='Action type (view, create, edit, delete, etc.)'
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text='Detailed description of what this permission allows'
    )
    
    # Hierarchy support
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
        help_text='Parent permission (for hierarchical permissions)'
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text='Inactive permissions cannot be assigned'
    )
    is_system = models.BooleanField(
        default=False,
        help_text='System permissions are predefined and cannot be modified'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'permissions'
        verbose_name = _('Permission')
        verbose_name_plural = _('Permissions')
        ordering = ['module', 'action']
        
        # Unique constraint: code must be unique per tenant
        constraints = [
            models.UniqueConstraint(
                fields=['tenant', 'code'],
                name='unique_tenant_permission_code'
            ),
        ]
        
        # Indexes for common queries
        indexes = [
            models.Index(fields=['tenant', 'module']),
            models.Index(fields=['tenant', 'is_active']),
        ]

    def __str__(self):
        return f"{self.code} ({self.tenant.code})"

    def save(self, *args, **kwargs):
        """
        Override save to ensure code is lowercase
        """
        self.code = self.code.lower()
        super().save(*args, **kwargs)

    @classmethod
    def get_by_module(cls, tenant, module):
        """
        Get all permissions for a specific module
        
        Args:
            tenant: Tenant instance
            module: Module name (e.g., 'tickets')
        
        Returns:
            QuerySet of Permission objects
        """
        return cls.objects.filter(
            tenant=tenant,
            module=module,
            is_active=True
        )

    @classmethod
    def get_by_action(cls, tenant, module, action):
        """
        Get specific permission by module and action
        
        Args:
            tenant: Tenant instance
            module: Module name
            action: Action name
        
        Returns:
            Permission object or None
        """
        return cls.objects.filter(
            tenant=tenant,
            module=module,
            action=action,
            is_active=True
        ).first()


class RolePermission(models.Model):
    """
    Relationship model between Role and Permission
    
    This is a through model that allows:
    - Assigning multiple permissions to a role
    - Tracking when permissions were assigned
    - Soft delete support via is_active flag
    """
    
    id = models.AutoField(primary_key=True)
    
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='permissions',
        help_text='Role that has this permission'
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='roles',
        help_text='Permission assigned to the role'
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text='Inactive role-permission relationships are ignored'
    )
    
    # Metadata
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by_id = models.IntegerField(
        null=True,
        blank=True,
        help_text='User ID who assigned this permission'
    )

    class Meta:
        db_table = 'role_permissions'
        verbose_name = _('Role Permission')
        verbose_name_plural = _('Role Permissions')
        
        # Unique constraint: each role can have each permission only once
        constraints = [
            models.UniqueConstraint(
                fields=['role', 'permission'],
                name='unique_role_permission'
            ),
        ]
        
        # Indexes for common queries
        indexes = [
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['permission']),
        ]

    def __str__(self):
        return f"{self.role.slug} -> {self.permission.code}"


class UserAccount(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    
    Features:
    - Multi-tenant support: Users belong to a tenant
    - UUID for external references
    - Enhanced security: password expiry, login attempts tracking
    - Profile information: phone, avatar, address
    - Status tracking: active, locked, verified
    
    Note: This extends AbstractUser, so it includes:
    - username, email, password, first_name, last_name
    - is_active, is_staff, is_superuser
    - last_login, date_joined
    """
    
    id = models.AutoField(primary_key=True)
    
    # UUID for external API references
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        help_text='Unique identifier for external API calls'
    )
    
    # Multi-tenant relationship
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='users',
        db_index=True,
        help_text='Tenant that owns this user'
    )
    
    # Profile information
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text='User phone number'
    )
    avatar = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text='URL to user avatar image'
    )
    address = models.TextField(
        blank=True,
        null=True,
        help_text='User address'
    )
    
    # Security
    is_locked = models.BooleanField(
        default=False,
        help_text='Locked users cannot login'
    )
    failed_login_attempts = models.IntegerField(
        default=0,
        help_text='Number of failed login attempts (resets on successful login)'
    )
    last_password_change = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Last time password was changed'
    )
    password_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Date when password expires and needs to be changed'
    )
    
    # Verification
    email_verified = models.BooleanField(
        default=False,
        help_text='Email address has been verified'
    )
    email_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Date when email was verified'
    )
    
    # Preferences
    language = models.CharField(
        max_length=10,
        default='vi',
        choices=[('vi', 'Tiếng Việt'), ('en', 'English')],
        help_text='Preferred language'
    )
    timezone = models.CharField(
        max_length=50,
        default='Asia/Ho_Chi_Minh',
        help_text='User timezone'
    )

    class Meta:
        db_table = 'user_accounts'
        verbose_name = _('User Account')
        verbose_name_plural = _('User Accounts')
        ordering = ['-date_joined']
        
        # Indexes for common queries
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['email']),
            models.Index(fields=['username']),
        ]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.tenant.code})"

    def get_roles(self):
        """
        Get all active roles assigned to this user
        
        Returns:
            QuerySet of Role objects
        """
        return self.roles.filter(is_active=True)

    def get_permissions(self):
        """
        Get all permissions from assigned roles
        
        Returns:
            QuerySet of Permission objects
        """
        return Permission.objects.filter(
            roles__role__users=self,
            is_active=True
        ).distinct()

    def get_permission_codes(self):
        """
        Get list of permission codes for this user
        
        Returns:
            List of permission codes
        """
        return list(self.get_permissions().values_list('code', flat=True))

    def has_permission(self, permission_code):
        """
        Check if user has specific permission
        
        Args:
            permission_code: Permission code (e.g., 'tickets.view')
        
        Returns:
            Boolean
        """
        if self.is_superuser:
            return True
        
        return self.get_permissions().filter(code=permission_code).exists()

    def has_module_permission(self, module):
        """
        Check if user has any permission in a module
        
        Args:
            module: Module name (e.g., 'tickets')
        
        Returns:
            Boolean
        """
        if self.is_superuser:
            return True
        
        return self.get_permissions().filter(module=module).exists()

    def has_any_permission(self, permission_codes):
        """
        Check if user has any of the given permissions
        
        Args:
            permission_codes: List of permission codes
        
        Returns:
            Boolean
        """
        if self.is_superuser:
            return True
        
        user_permissions = set(self.get_permission_codes())
        return bool(user_permissions.intersection(set(permission_codes)))

    def has_all_permissions(self, permission_codes):
        """
        Check if user has all given permissions
        
        Args:
            permission_codes: List of permission codes
        
        Returns:
            Boolean
        """
        if self.is_superuser:
            return True
        
        user_permissions = set(self.get_permission_codes())
        return user_permissions.issuperset(set(permission_codes))

    def lock_account(self):
        """
        Lock user account (prevent login)
        """
        self.is_locked = True
        self.save(update_fields=['is_locked'])

    def unlock_account(self):
        """
        Unlock user account (allow login)
        """
        self.is_locked = False
        self.failed_login_attempts = 0
        self.save(update_fields=['is_locked', 'failed_login_attempts'])

    def increment_failed_login(self):
        """
        Increment failed login attempts
        Lock account if exceeds MAX_LOGIN_ATTEMPTS
        """
        from django.conf import settings
        
        max_attempts = getattr(settings, 'MAX_LOGIN_ATTEMPTS', 5)
        self.failed_login_attempts += 1
        
        if self.failed_login_attempts >= max_attempts:
            self.is_locked = True
        
        self.save(update_fields=['failed_login_attempts', 'is_locked'])

    def reset_failed_login(self):
        """
        Reset failed login attempts after successful login
        """
        self.failed_login_attempts = 0
        self.save(update_fields=['failed_login_attempts'])


class UserRole(models.Model):
    """
    Relationship model between User and Role
    
    Features:
    - Assign multiple roles to a user
    - Track role assignment history
    - Soft delete support via is_active flag
    """
    
    id = models.AutoField(primary_key=True)
    
    user = models.ForeignKey(
        UserAccount,
        on_delete=models.CASCADE,
        related_name='roles',
        help_text='User assigned to this role'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='users',
        help_text='Role assigned to the user'
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text='Inactive user-role relationships are ignored'
    )
    
    # Metadata
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by_id = models.IntegerField(
        null=True,
        blank=True,
        help_text='User ID who assigned this role'
    )

    class Meta:
        db_table = 'user_roles'
        verbose_name = _('User Role')
        verbose_name_plural = _('User Roles')
        
        # Unique constraint: each user can have each role only once
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'role'],
                name='unique_user_role'
            ),
        ]
        
        # Indexes for common queries
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.role.slug}"


class UserSession(models.Model):
    """
    Track user sessions for security and audit purposes
    
    Features:
    - Track login/logout
    - Device and IP information
    - Session timeout
    - Concurrent session management
    """
    
    id = models.AutoField(primary_key=True)
    
    user = models.ForeignKey(
        UserAccount,
        on_delete=models.CASCADE,
        related_name='sessions',
        help_text='User who owns this session'
    )
    
    # Session identification
    token = models.CharField(
        max_length=500,
        unique=True,
        db_index=True,
        help_text='Session token for authentication'
    )
    
    # Device and location information
    ip_address = models.GenericIPAddressField(
        help_text='IP address of the user'
    )
    user_agent = models.TextField(
        help_text='User agent string (browser/device info)'
    )
    device_info = models.JSONField(
        default=dict,
        blank=True,
        help_text='Parsed device information'
    )
    
    # Session timing
    expires_at = models.DateTimeField(
        help_text='Session expiration time'
    )
    last_activity = models.DateTimeField(
        auto_now=True,
        help_text='Last activity timestamp'
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text='Session is still active'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_sessions'
        verbose_name = _('User Session')
        verbose_name_plural = _('User Sessions')
        ordering = ['-created_at']
        
        # Indexes for common queries
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['token']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.ip_address}"

    def is_expired(self):
        """
        Check if session has expired
        """
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def invalidate(self):
        """
        Invalidate this session (logout)
        """
        self.is_active = False
        self.save(update_fields=['is_active'])


class PasswordResetToken(models.Model):
    """
    Password reset token model
    
    Features:
    - One-time use tokens
    - Expiration support
    - Track used tokens
    """
    
    id = models.AutoField(primary_key=True)
    
    user = models.ForeignKey(
        UserAccount,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
        help_text='User requesting password reset'
    )
    
    # Token
    token = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text='Reset token (one-time use)'
    )
    
    # Expiration
    expires_at = models.DateTimeField(
        help_text='Token expiration time'
    )
    used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When token was used'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'password_reset_tokens'
        verbose_name = _('Password Reset Token')
        verbose_name_plural = _('Password Reset Tokens')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"

    def is_expired(self):
        """
        Check if token has expired
        """
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def is_used(self):
        """
        Check if token has been used
        """
        return self.used_at is not None

    def mark_as_used(self):
        """
        Mark token as used (one-time use)
        """
        from django.utils import timezone
        self.used_at = timezone.now()
        self.save(update_fields=['used_at'])