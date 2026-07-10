from django.shortcuts import render


def password_reset_confirm(request):
    return render(request, "pages/auth/password_reset_confirm.html")
