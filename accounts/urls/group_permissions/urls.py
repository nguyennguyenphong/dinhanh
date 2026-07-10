from django.urls import path

from accounts.views import group_permissions as group_permission_views

urlpatterns = [
    path(
        "group_permissions/list/ui/",
        group_permission_views.PermissionGroupListView.as_view(),
        name="group_permission_list",
    ),
    path(
        "group_permissions/list/api/",
        group_permission_views.PermissionGroupListApiView.as_view(),
        name="group_permission_list_api",
    ),
    path(
        "group_permissions/create/",
        group_permission_views.PermissionGroupCreateView.as_view(),
        name="group_permission_create",
    ),
    path(
        "group_permissions/update/<int:pk>/",
        group_permission_views.PermissionGroupUpdateView.as_view(),
        name="group_permission_update",
    ),
    path(
        "group_permissions/delete/<int:pk>/",
        group_permission_views.PermissionGroupDeleteView.as_view(),
        name="group_permission_delete",
    ),
    # Fallback/Backward compatibility names
    path(
        "group_permissions/list/",
        group_permission_views.PermissionGroupListView.as_view(),
        name="group_permissions_list",
    ),
    path(
        "group_permissions/create_fallback/",
        group_permission_views.PermissionGroupCreateView.as_view(),
        name="group_permissions_create",
    ),
]
