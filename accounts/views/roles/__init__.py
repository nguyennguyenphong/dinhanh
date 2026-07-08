from accounts.views.roles.create import RoleCreateView
from accounts.views.roles.update import RoleUpdateView
from accounts.views.roles.delete import RoleDeleteView
from accounts.views.roles.detail import RoleDetailView
from accounts.views.roles.list import RoleListView, RoleListApiView

__all__ = [
    "RoleCreateView",
    "RoleUpdateView",
    "RoleDeleteView",
    "RoleDetailView",
    "RoleListView",
    "RoleListApiView",
]
