from __future__ import annotations

from django.contrib import admin

from accounts.models import (
    Permission,
    PermissionGroup,
    Role,
    SessionAuditLog,
    UserAccount,
    UserSession,
)


@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "full_name",
        "tenant",
        "branch",
        "is_active",
        "is_staff",
    )
    list_filter = ("is_active", "is_staff", "tenant")
    search_fields = ("username", "email", "full_name", "tenant__name")
    readonly_fields = ("uuid", "last_login")
    ordering = ("tenant", "username")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "tenant", "is_system", "is_active")
    list_filter = ("is_system", "is_active", "tenant")
    search_fields = ("name", "slug", "tenant__name")
    ordering = ("tenant", "name")


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = (
        "codename",
        "name",
        "module",
        "action",
        "tenant",
        "is_system",
        "is_active",
    )
    list_filter = ("module", "action", "is_system", "is_active", "tenant")
    search_fields = ("codename", "name", "module", "tenant__name")
    ordering = ("tenant", "codename")


@admin.register(PermissionGroup)
class PermissionGroupAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "tenant", "is_active")
    list_filter = ("is_active", "tenant")
    search_fields = ("code", "name", "tenant__name")
    ordering = ("tenant", "code")


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "ip_address",
        "user_agent",
        "is_active",
        "created_at",
        "expires_at",
    )
    list_filter = ("is_active", "created_at")
    search_fields = ("user__email", "ip_address")
    ordering = ("-created_at",)


@admin.register(SessionAuditLog)
class SessionAuditLogAdmin(admin.ModelAdmin):
    list_display = ("session", "action", "ip_address", "timestamp")
    list_filter = ("action", "timestamp")
    search_fields = ("session__user__email", "ip_address")
    ordering = ("-timestamp",)
