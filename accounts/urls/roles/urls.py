# Url role's module
from django.urls import path

from accounts.views.roles.create import create
from accounts.views.roles.list import list

urlpatterns = [
    path("list/", list, name="role_list"),
    path("create/", create, name="role_create"),
]
