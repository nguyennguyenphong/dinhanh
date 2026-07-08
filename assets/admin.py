from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from assets.models import Asset, AssetCategory, StorageUnit


@admin.register(AssetCategory)
class AssetCategoryAdmin(admin.ModelAdmin):
    list_display = ("tenant", "name", "created_at", "updated_at")
    list_filter = ("tenant",)
    search_fields = ("name", "tenant__name")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("tenant", "name")


@admin.register(StorageUnit)
class StorageUnitAdmin(admin.ModelAdmin):
    list_display = ("tenant", "code", "name", "branch", "created_at")
    list_filter = ("tenant", "branch")
    search_fields = ("code", "name", "tenant__name", "branch__name")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("tenant", "code")


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "tenant",
        "category",
        "branch",
        "purchase_price",
        "current_value",
        "status",
        "created_at",
    )
    list_filter = ("status", "tenant", "category", "branch")
    search_fields = ("code", "name", "serial_number", "tenant__name")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("-created_at",)

    fieldsets = (
        (
            _("Identity & Multi-Tenancy"),
            {
                "fields": (
                    "tenant",
                    "category",
                    "code",
                    "name",
                    "serial_number",
                ),
            },
        ),
        (
            _("Custody & Logistics"),
            {
                "fields": (
                    "branch",
                    "assigned_to",
                ),
            },
        ),
        (
            _("Financials & Valuation"),
            {
                "fields": (
                    "purchase_date",
                    "purchase_price",
                    "depreciation_rate",
                    "current_value",
                    "warranty_expiry",
                ),
            },
        ),
        (
            _("Operational State & Details"),
            {
                "fields": (
                    "status",
                    "notes",
                ),
            },
        ),
    )
