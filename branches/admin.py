from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from branches.models import Branch, BranchAuditLog


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "tenant",
        "phone",
        "email",
        "manager",
        "timezone",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "tenant", "timezone")
    search_fields = ("code", "name", "phone", "email", "tenant__name")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("tenant", "code")

    fieldsets = (
        (
            _("Identity & Tenant ownership"),
            {
                "fields": (
                    "tenant",
                    "code",
                    "name",
                ),
            },
        ),
        (
            _("Contact & Custody details"),
            {
                "fields": (
                    "address",
                    "phone",
                    "email",
                    "manager",
                ),
            },
        ),
        (
            _("Location, Timing & State"),
            {
                "fields": (
                    "latitude",
                    "longitude",
                    "timezone",
                    "is_active",
                ),
            },
        ),
        (
            _("Advanced Metadata configuration"),
            {
                "fields": ("metadata",),
            },
        ),
    )


@admin.register(BranchAuditLog)
class BranchAuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "branch",
        "action",
        "created_by",
        "created_at",
    )
    list_filter = ("action", "created_at")
    search_fields = ("branch__name", "user__email", "new_values")
    readonly_fields = ("branch", "action", "created_by", "new_values", "created_at")
    ordering = ("-created_at",)
