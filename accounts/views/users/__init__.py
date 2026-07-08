from accounts.views.users.create import UserCreateView
from accounts.views.users.update import UserUpdateView
from accounts.views.users.delete import UserDeleteView
from accounts.views.users.detail import UserDetailView
from accounts.views.users.list import UserListView, UserListApiView

__all__ = [
    "UserCreateView",
    "UserUpdateView",
    "UserDeleteView",
    "UserDetailView",
    "UserListView",
    "UserListApiView",
]
