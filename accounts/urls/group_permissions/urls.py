from django.urls import path

from accounts.views import group_permissions as group_permission_views

urlpatterns = [
    path(
        "list/ui/",
        group_permission_views.PermissionGroupListView.as_view(),
        name="group_permission_list",
    ),
    path(
        "list/api/",
        group_permission_views.PermissionGroupListApiView.as_view(),
        name="group_permission_list_api",
    ),
    path(
        "create/",
        group_permission_views.PermissionGroupCreateView.as_view(),
        name="group_permission_create",
    ),
    path(
        "update/<int:pk>/",
        group_permission_views.PermissionGroupUpdateView.as_view(),
        name="group_permission_update",
    ),
    path(
        "delete/<int:pk>/",
        group_permission_views.PermissionGroupDeleteView.as_view(),
        name="group_permission_delete",
    ),
    # Fallback/Backward compatibility names
    path(
        "list/",
        group_permission_views.PermissionGroupListView.as_view(),
        name="group_permissions_list",
    ),
    path(
        "create_fallback/",
        group_permission_views.PermissionGroupCreateView.as_view(),
        name="group_permissions_create",
    ),
]
