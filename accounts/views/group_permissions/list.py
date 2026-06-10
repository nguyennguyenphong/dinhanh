# Path: accounts/views/group_permissions/list.py

from django.shortcuts import render


def list(request):
    return render(request, "pages/group_permission_list.html")
