# Url permission's module
from django.urls import path

from accounts.views.permissions.create import create
from accounts.views.permissions.list import list

urlpatterns = [
    path("list/", list, name="permission_list"),
    path("create/", create, name="permission_create"),
]
