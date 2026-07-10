from django.shortcuts import redirect, render


def password_reset_complete(request):
    if request.user.is_authenticated:
        return redirect("/")
    return render(request, "pages/auth/password_reset_complete.html")
