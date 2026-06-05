# Path: accounts/views/roles/list.py

from django.shortcuts import render


def list(request):
    return render(request, "pages/role_list.html")
