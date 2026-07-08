from django.urls import path

from accounts.views import users as user_views

urlpatterns = [
    path("list/ui/", user_views.UserListView.as_view(), name="user_list"),
    path("list/api/", user_views.UserListApiView.as_view(), name="user_list_api"),
    path("create/", user_views.UserCreateView.as_view(), name="user_create"),
    path("update/<int:pk>/", user_views.UserUpdateView.as_view(), name="user_update"),
    path("detail/<int:pk>/", user_views.UserDetailView.as_view(), name="user_detail"),
    path("delete/<int:pk>/", user_views.UserDeleteView.as_view(), name="user_delete"),
]
