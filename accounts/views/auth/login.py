# Path: accounts/views/login.py

from django.shortcuts import render

from accounts.views.forms import LoginBaseForm


def login(request):
    form = LoginBaseForm()
    return render(request, "pages/login.html", {"form": form})
