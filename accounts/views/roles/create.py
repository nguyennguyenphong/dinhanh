# Path: accounts/views/roles/create.py

from django.shortcuts import render


def create(request):
    return render(request, "pages/role_create.html")