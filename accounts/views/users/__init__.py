from accounts.views.users.user_create_view import UserCreateView
from accounts.views.users.user_detail_view import UserDetailView
from accounts.views.users.user_list_view import UserListApiView, UserListView
from accounts.views.users.user_update_view import UserUpdateView
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
