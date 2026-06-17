from django.shortcuts import render

from accounts.views.forms import RegisterBaseForm


def register(request):
    form = RegisterBaseForm()

    return render(request, "pages/register.html", {"form": form})
