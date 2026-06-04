from django.urls import include, path

urlpatterns = [
    path("roles/", include("accounts.urls.roles.urls")),
    path("auth/", include("accounts.urls.auth.urls")),
    path("permissions/", include("accounts.urls.permissions.urls")),
    path("group_permissions/", include("accounts.urls.group_permissions.urls")),
]