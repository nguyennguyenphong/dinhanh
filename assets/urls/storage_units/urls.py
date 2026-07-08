from django.urls import path

from assets.views import storage_units as storage_unit_views

urlpatterns = [
    # -------------------------------------------------------------------------
    # 1. LIST FUNCTION
    # -------------------------------------------------------------------------
    path(
        "storage_units/list/ui/",
        storage_unit_views.StorageUnitListView.as_view(),
        name="storage_unit_list",
    ),
    path(
        "storage_units/list/api/",
        storage_unit_views.StorageUnitListApiView.as_view(),
        name="storage_unit_list_api",
    ),
    # -------------------------------------------------------------------------
    # 2. CREATE FUNCTION
    # -------------------------------------------------------------------------
    path(
        "storage_units/create/",
        storage_unit_views.StorageUnitCreateView.as_view(),
        name="storage_unit_create",
    ),
    # -------------------------------------------------------------------------
    # 3. UPDATE FUNCTION
    # -------------------------------------------------------------------------
    path(
        "storage_units/update/<uuid:pk>/",
        storage_unit_views.StorageUnitUpdateView.as_view(),
        name="storage_unit_update",
    ),
    # -------------------------------------------------------------------------
    # 4. DETAIL FUNCTION
    # -------------------------------------------------------------------------
    path(
        "storage_units/detail/<uuid:pk>/",
        storage_unit_views.StorageUnitDetailView.as_view(),
        name="storage_unit_detail",
    ),
    # -------------------------------------------------------------------------
    # 5. DELETE FUNCTION
    # -------------------------------------------------------------------------
    path(
        "storage_units/delete/<uuid:pk>/",
        storage_unit_views.StorageUnitDeleteView.as_view(),
        name="storage_unit_delete",
    ),
]
