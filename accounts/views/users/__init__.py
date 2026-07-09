from accounts.views.users.create import UserCreateView
from accounts.views.users.detail import UserDetailView
from accounts.views.users.list import UserListApiView, UserListView
from accounts.views.users.update import UserUpdateView
from accounts.views.users.user_hard_delete_view import UserHardDeleteView
from accounts.views.users.user_soft_delete_view import UserSoftDeleteView

# Alias for backward compatibility if referenced elsewhere
UserDeleteView = UserSoftDeleteView

__all__ = [
    "UserCreateView",
    "UserUpdateView",
    "UserDeleteView",
    "UserSoftDeleteView",
    "UserHardDeleteView",
    "UserDetailView",
    "UserListView",
    "UserListApiView",
]
