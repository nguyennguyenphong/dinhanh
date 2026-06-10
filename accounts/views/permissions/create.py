# Path: accounts/views/permissions/create.py

from django.shortcuts import render


def create(request):
    return render(request, "pages/permission_create.html")
