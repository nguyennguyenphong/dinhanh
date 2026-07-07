from django.urls import include, path

from tenants.views import (
    TenantAuditLogListView,
    TenantInvitationAcceptView,
    TenantInvitationListView,
)

urlpatterns = [
    # 1. Tenant CRUD views (UI + API)
    path("", include("tenants.urls.tenants.urls")),
    # 2. Feature Flag views
    path("", include("tenants.urls.tenant_feature_flag.urls")),
    # 3. Invitation views
    path(
        "tenants/<int:pk>/invitations/",
        TenantInvitationListView.as_view(),
        name="tenant-invitation-list",
    ),
    path(
        "invitations/accept/",
        TenantInvitationAcceptView.as_view(),
        name="tenant-invitation-accept",
    ),
    # 4. Audit Log views
    path(
        "tenants/<int:pk>/audit-logs/",
        TenantAuditLogListView.as_view(),
        name="tenant-audit-log-list",
    ),
]
