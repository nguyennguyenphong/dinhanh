from django.contrib import messages
from django.contrib.auth import logout as django_logout
from django.shortcuts import redirect


def logout(request):
    """
    Handles logging out the authenticated user.
    Logs out from Django, clears user session, and redirects to the login page.
    """
    if request.user.is_authenticated:
        django_logout(request)
        messages.success(request, "Đăng xuất thành công.")
    return redirect("login")
