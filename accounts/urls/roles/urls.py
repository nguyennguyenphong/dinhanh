from django.urls import path

from accounts.views import roles as role_views

urlpatterns = [
    path("list/ui/", role_views.RoleListView.as_view(), name="role_list"),
    path("list/api/", role_views.RoleListApiView.as_view(), name="role_list_api"),
    path("create/", role_views.RoleCreateView.as_view(), name="role_create"),
    path("update/<int:pk>/", role_views.RoleUpdateView.as_view(), name="role_update"),
    path("detail/<int:pk>/", role_views.RoleDetailView.as_view(), name="role_detail"),
    path("delete/<int:pk>/", role_views.RoleDeleteView.as_view(), name="role_delete"),
]
