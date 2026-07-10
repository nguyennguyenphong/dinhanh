from accounts.views.permissions.permission_create_view import PermissionCreateView
from accounts.views.permissions.permission_soft_delete_view import PermissionDeleteView
from accounts.views.permissions.permission_list_view import PermissionListApiView, PermissionListView
from accounts.views.permissions.permission_update_view import PermissionUpdateView

__all__ = [
    "PermissionCreateView",
    "PermissionUpdateView",
    "PermissionDeleteView",
    "PermissionListView",
    "PermissionListApiView",
]
