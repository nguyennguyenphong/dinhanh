from django.urls import path

from accounts.views import roles as role_views

urlpatterns = [
    path("roles/list/ui/", role_views.RoleListView.as_view(), name="role_list"),
    path("roles/list/api/", role_views.RoleListApiView.as_view(), name="role_list_api"),
    path("roles/create/", role_views.RoleCreateView.as_view(), name="role_create"),
    path("roles/update/<int:pk>/", role_views.RoleUpdateView.as_view(), name="role_update"),
    path("roles/detail/<int:pk>/", role_views.RoleDetailView.as_view(), name="role_detail"),
    path(
        "roles/delete/<int:pk>/", role_views.RoleSoftDeleteView.as_view(), name="role_delete"
    ),
    path(
        "roles/hard-delete/<int:pk>/",
        role_views.RoleHardDeleteView.as_view(),
        name="role_hard_delete",
    ),
]
