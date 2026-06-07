"""
Django admin configuration for the Tenant bounded context.
Provides full CRUD with search, filtering, and inline audit/flag display.
"""
from __future__ import annotations

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from tenants.models import (
        Tenant,
        TenantAuditLog,
        TenantFeatureFlag,
        TenantInvitation,
    )


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "plan_badge",
        "is_active",
        "currency",
        "max_users",
        "subscription_expires_at",
        "created_at",
    )
    list_filter = ("plan", "is_active", "currency", "default_language")
    search_fields = ("code", "name", "domain")
    readonly_fields = ("uuid", "created_at", "updated_at")
    ordering = ("-created_at",)

    fieldsets = (
        (
            _("Identity"),
            {
                "fields": ("uuid", "code", "name", "domain", "logo_url", "primary_color"),
            },
        ),
        (
            _("Plan & Subscription"),
            {
                "fields": (
                    "plan",
                    "is_active",
                    "subscription_started_at",
                    "subscription_expires_at",
                    "max_users",
                    "max_branches",
                    "max_vehicles",
                ),
            },
        ),
        (
            _("Localisation"),
            {
                "fields": ("currency", "exchange_rate", "default_language", "timezone"),
            },
        ),
        (
            _("Settings"),
            {"fields": ("settings",), "classes": ("collapse",)},
        ),
        (
            _("Timestamps"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    @admin.display(description=_("Plan"))
    def plan_badge(self, obj):
        colors = {
            "TRIAL": "#6B7280",
            "STANDARD": "#3B82F6",
            "PROFESSIONAL": "#8B5CF6",
            "ENTERPRISE": "#F59E0B",
        }
        color = colors.get(obj.plan, "#6B7280")
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:4px;">{}</span>',
            color,
            obj.plan,
        )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("tenant_feature_flags")


@admin.register(TenantAuditLog)
class TenantAuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "tenant",
        "action",
        "module",
        "object_type",
        "username",
        "status",
        "ip_address",
        "created_at",
    )
    list_filter = ("action", "module", "status")
    search_fields = ("tenant__code", "username", "object_repr")
    readonly_fields = (
        "tenant",
        "user_id",
        "username",
        "action",
        "module",
        "object_type",
        "object_id",
        "object_repr",
        "old_values",
        "new_values",
        "changes",
        "ip_address",
        "user_agent",
        "status",
        "error_message",
        "created_at",
    )
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(TenantFeatureFlag)
class TenantFeatureFlagAdmin(admin.ModelAdmin):
    list_display = (
        "tenant",
        "code",
        "name",
        "is_enabled",
        "rollout_percentage",
        "updated_at",
    )
    list_filter = ("is_enabled", "tenant")
    search_fields = ("code", "name", "tenant__code")
    readonly_fields = ("created_at", "updated_at")


@admin.register(TenantInvitation)
class TenantInvitationAdmin(admin.ModelAdmin):
    list_display = (
        "tenant",
        "email",
        "status",
        "invited_by_id",
        "expires_at",
        "accepted_at",
        "created_at",
    )
    list_filter = ("status", "tenant")
    search_fields = ("email", "tenant__code")
    readonly_fields = ("token", "created_at", "accepted_at")
