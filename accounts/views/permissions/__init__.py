from accounts.views.permissions.create import PermissionCreateView
from accounts.views.permissions.delete import PermissionDeleteView
from accounts.views.permissions.list import PermissionListApiView, PermissionListView
from accounts.views.permissions.update import PermissionUpdateView

__all__ = [
    "PermissionCreateView",
    "PermissionUpdateView",
    "PermissionDeleteView",
    "PermissionListView",
    "PermissionListApiView",
]
