from accounts.urls.auth.urls import urlpatterns as auth_patterns
from accounts.urls.group_permissions.urls import urlpatterns as group_permission_patterns
from accounts.urls.permissions.urls import urlpatterns as permission_patterns
from accounts.urls.roles.urls import urlpatterns as role_patterns
from accounts.urls.users.urls import urlpatterns as user_patterns

urlpatterns = [
    *auth_patterns,
    *group_permission_patterns,
    *permission_patterns,
    *role_patterns,
    *user_patterns,
]
