from django.urls import path
from tenants.views import tenants as tenant_views

urlpatterns = [
    # -------------------------------------------------------------------------
    # 1. LIST FUNCTION
    # -------------------------------------------------------------------------
    path("list/ui/", tenant_views.TenantListView.as_view(), name="tenant_list"),
    
    # -------------------------------------------------------------------------
    # 2. CREATE FUNCTION (Split into UI Presentation and Data Persistence)
    # -------------------------------------------------------------------------
    path("create/", tenant_views.TenantCreateView.as_view(), name="tenant_create"),
    
    # -------------------------------------------------------------------------
    # 3. UPDATE FUNCTION (Handles both GET for UI prep and POST for processing)
    # -------------------------------------------------------------------------
    path("update/<int:pk>/", tenant_views.TenantUpdateView.as_view(), name="tenant_update"),
    
    # -------------------------------------------------------------------------
    # 4. DELETE FUNCTION (Enforced via secure POST action forms)
    # -------------------------------------------------------------------------
    path("delete/<int:pk>/", tenant_views.TenantSoftDeleteView.as_view(), name="tenant_delete"),

    # -------------------------------------------------------------------------
    # 5. DETAIL FUNCTION (Handles both GET for UI prep and POST for processing)
    # -------------------------------------------------------------------------
    path("detail/<int:pk>/", tenant_views.TenantDetailView.as_view(), name="tenant_detail"),
]