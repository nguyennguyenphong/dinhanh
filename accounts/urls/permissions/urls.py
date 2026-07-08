from django.urls import path

from accounts.views import permissions as permission_views

urlpatterns = [
    path(
        "list/ui/",
        permission_views.PermissionListView.as_view(),
        name="permission_list",
    ),
    path(
        "list/api/",
        permission_views.PermissionListApiView.as_view(),
        name="permission_list_api",
    ),
    path(
        "create/",
        permission_views.PermissionCreateView.as_view(),
        name="permission_create",
    ),
    path(
        "update/<int:pk>/",
        permission_views.PermissionUpdateView.as_view(),
        name="permission_update",
    ),
    path(
        "delete/<int:pk>/",
        permission_views.PermissionDeleteView.as_view(),
        name="permission_delete",
    ),
]
