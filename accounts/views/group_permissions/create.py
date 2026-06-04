# Path: accounts/views/group_permissions/create.py

from django.shortcuts import render


def create(request):
    return render(request, "pages/group_permission_create.html")