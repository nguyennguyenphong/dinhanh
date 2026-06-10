"""
URL configuration for the Tenant bounded context.

Include in your project's root urls.py:
    path("api/v1/", include("tenants.urls")),
"""

from django.urls import path

from tenants.views import (
    FeatureFlagDetailView,
    FeatureFlagListView,
)

app_name = "tenants"

urlpatterns = [
    path(
        "tenants/<int:pk>/feature-flags/",
        FeatureFlagListView.as_view(),
        name="tenant-feature-flag-list",
    ),
    path(
        "tenants/<int:pk>/feature-flags/<str:code>/",
        FeatureFlagDetailView.as_view(),
        name="tenant-feature-flag-detail",
    ),
]
