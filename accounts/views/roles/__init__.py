from accounts.views.roles.role_create_view import RoleCreateView
from accounts.views.roles.role_detail_view import RoleDetailView
from accounts.views.roles.role_hard_delete_view import RoleHardDeleteView
from accounts.views.roles.role_list_view import RoleListApiView, RoleListView
from accounts.views.roles.role_soft_delete_view import RoleSoftDeleteView
from accounts.views.roles.role_update_view import RoleUpdateView

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
