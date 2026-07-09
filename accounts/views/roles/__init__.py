from accounts.views.roles.create import RoleCreateView
from accounts.views.roles.detail import RoleDetailView
from accounts.views.roles.list import RoleListApiView, RoleListView
from accounts.views.roles.update import RoleUpdateView
from accounts.views.roles.role_soft_delete_view import RoleSoftDeleteView
from accounts.views.roles.role_hard_delete_view import RoleHardDeleteView

RoleDeleteView = RoleSoftDeleteView

__all__ = [
    "RoleCreateView",
    "RoleUpdateView",
    "RoleDeleteView",
    "RoleSoftDeleteView",
    "RoleHardDeleteView",
    "RoleDetailView",
    "RoleListView",
    "RoleListApiView",
]
