from django.urls import path

from branches.views import branches as branches_views

urlpatterns = [
    # -------------------------------------------------------------------------
    # 1. LIST FUNCTION
    # -------------------------------------------------------------------------
    path(
        "branches/list/ui/",
        branches_views.BranchListView.as_view(),
        name="branch_list",
    ),
    # -------------------------------------------------------------------------
    # 2. CREATE FUNCTION (Split into UI Presentation and Data Persistence)
    # -------------------------------------------------------------------------
    path(
        "branches/create/",
        branches_views.BranchCreateView.as_view(),
        name="branch_create",
    ),
    # -------------------------------------------------------------------------
    # 3. UPDATE FUNCTION (Handles both GET for UI prep and POST for processing)
    # -------------------------------------------------------------------------
    path(
        "branches/update/<uuid:pk>/",
        branches_views.BranchUpdateView.as_view(),
        name="branch_update",
    ),
    # -------------------------------------------------------------------------
    # 4. DETAIL FUNCTION (Handles both GET for UI prep and POST for processing)
    # -------------------------------------------------------------------------
    path(
        "branches/detail/<uuid:pk>/",
        branches_views.BranchDetailView.as_view(),
        name="branch_detail",
    ),
]
