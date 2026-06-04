# Url group permission's module
from django.urls import path

from accounts.views.group_permissions.list import list
from accounts.views.group_permissions.create import create

urlpatterns = [
    path("list/", list, name="group_permissions_list"),
    path("create/", create, name="group_permissions_create"),
]
