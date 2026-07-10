from django.urls import path

from accounts.views import users as user_views

urlpatterns = [
    path("users/list/ui/", user_views.UserListView.as_view(), name="user_list"),
    path("users/list/api/", user_views.UserListApiView.as_view(), name="user_list_api"),
    path("users/create/", user_views.UserCreateView.as_view(), name="user_create"),
    path("users/update/<int:pk>/", user_views.UserUpdateView.as_view(), name="user_update"),
    path("users/detail/<int:pk>/", user_views.UserDetailView.as_view(), name="user_detail"),
    path(
        "users/delete/<int:pk>/", user_views.UserSoftDeleteView.as_view(), name="user_delete"
    ),
    path(
        "users/hard-delete/<int:pk>/",
        user_views.UserHardDeleteView.as_view(),
        name="user_hard_delete",
    ),
]
