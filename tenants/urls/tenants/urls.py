from django.urls import path

from tenants.views import tenants as tenant_views

urlpatterns = [
    # -------------------------------------------------------------------------
    # 1. LIST FUNCTION
    # -------------------------------------------------------------------------
    path("list/ui/", tenant_views.TenantListView.as_view(), name="tenant_list"),
    path(
        "api/v1/list/", tenant_views.TenantListApiView.as_view(), name="tenant_list_api"
    ),
    # -------------------------------------------------------------------------
    # 2. CREATE FUNCTION (Split into UI Presentation and Data Persistence)
    # -------------------------------------------------------------------------
    path("create/", tenant_views.TenantCreateView.as_view(), name="tenant_create"),
    # -------------------------------------------------------------------------
    # 3. UPDATE FUNCTION (Handles both GET for UI prep and POST for processing)
    # -------------------------------------------------------------------------
    path(
        "update/<uuid:pk>/",
        tenant_views.TenantUpdateView.as_view(),
        name="tenant_update",
    ),
    # -------------------------------------------------------------------------
    # 4. SOFT DELETE FUNCTION (Enforced via secure POST action forms)
    # -------------------------------------------------------------------------
    path(
        "soft_delete/<uuid:pk>/",
        tenant_views.TenantSoftDeleteView.as_view(),
        name="tenant_soft_delete",
    ),
    # -------------------------------------------------------------------------
    # 5. DETAIL FUNCTION (Handles both GET for UI prep and POST for processing)
    # -------------------------------------------------------------------------
    path(
        "detail/<uuid:pk>/",
        tenant_views.TenantDetailView.as_view(),
        name="tenant_detail",
    ),
    # -------------------------------------------------------------------------
    # 6. HARD DELETE FUNCTION (Enforced via secure POST action forms)
    # -------------------------------------------------------------------------
    path(
        "hard_delete/<uuid:pk>/",
        tenant_views.TenantHardDeleteView.as_view(),
        name="tenant_hard_delete",
    ),
]
