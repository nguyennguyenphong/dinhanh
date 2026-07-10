from django.urls import path

from accounts.views import permissions as permission_views

urlpatterns = [
    path(
        "permissions/list/ui/",
        permission_views.PermissionListView.as_view(),
        name="permission_list",
    ),
    path(
        "permissions/list/api/",
        permission_views.PermissionListApiView.as_view(),
        name="permission_list_api",
    ),
    path(
        "permissions/create/",
        permission_views.PermissionCreateView.as_view(),
        name="permission_create",
    ),
    path(
        "permissions/update/<int:pk>/",
        permission_views.PermissionUpdateView.as_view(),
        name="permission_update",
    ),
    path(
        "permissions/delete/<int:pk>/",
        permission_views.PermissionDeleteView.as_view(),
        name="permission_delete",
    ),
]
