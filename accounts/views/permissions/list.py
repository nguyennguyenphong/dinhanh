# Path: accounts/views/permissions/list.py

from django.shortcuts import render


def list(request):
    return render(request, "pages/permission_list.html")
