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
    path(
        "branches/list/api/",
        branches_views.BranchListApiView.as_view(),
        name="branch_list_api",
    ),
    # -------------------------------------------------------------------------
    # 2. CREATE FUNCTION
    # -------------------------------------------------------------------------
    path(
        "branches/create/",
        branches_views.BranchCreateView.as_view(),
        name="branch_create",
    ),
    # -------------------------------------------------------------------------
    # 3. UPDATE FUNCTION
    # -------------------------------------------------------------------------
    path(
        "branches/update/<int:pk>/",
        branches_views.BranchUpdateView.as_view(),
        name="branch_update",
    ),
    # -------------------------------------------------------------------------
    # 4. DETAIL FUNCTION
    # -------------------------------------------------------------------------
    path(
        "branches/detail/<int:pk>/",
        branches_views.BranchDetailView.as_view(),
        name="branch_detail",
    ),
    # -------------------------------------------------------------------------
    # 5. DELETE FUNCTION
    # -------------------------------------------------------------------------
    path(
        "branches/delete/<int:pk>/",
        branches_views.BranchDeleteView.as_view(),
        name="branch_delete",
    ),
]
