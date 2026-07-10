from django.shortcuts import render


def password_reset(request):
    return render(request, "pages/auth/password_reset.html")
