from django.urls import path
from tenants.views import tenants as tenant_views

urlpatterns = [
    # -------------------------------------------------------------------------
    # 1. LIST FUNCTION
    # -------------------------------------------------------------------------
    path("list/ui/", tenant_views.list_tenant, name="tenant_list"),
    
    # -------------------------------------------------------------------------
    # 2. CREATE FUNCTION (Split into UI Presentation and Data Persistence)
    # -------------------------------------------------------------------------
    path("create/ui/", tenant_views.tenant_create_ui, name="tenant_create_ui"),
    path("create/", tenant_views.create_tenant_execute, name="tenant_create_execute"),
    
    # -------------------------------------------------------------------------
    # 3. UPDATE FUNCTION (Handles both GET for UI prep and POST for processing)
    # -------------------------------------------------------------------------
    path("update/<int:pk>/", tenant_views.TenantUpdateView.as_view(), name="tenant_update"),
    
    # -------------------------------------------------------------------------
    # 4. DELETE FUNCTION (Enforced via secure POST action forms)
    # -------------------------------------------------------------------------
    path("delete/<int:pk>/", tenant_views.TenantDeleteView.as_view(), name="tenant_delete"),
]