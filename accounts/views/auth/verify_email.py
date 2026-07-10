from django.contrib import messages
from django.shortcuts import redirect, render

from accounts.application.dtos.auth.auth_dto import VerifyEmailDto
from accounts.providers.auth.auth_provider import AuthProvider
from accounts.views.forms import VerifyEmailForm


def verify_email(request):
    if request.user.is_authenticated:
        return redirect("/")

    email = request.GET.get("email", "")

    if request.method == "POST":
        form = VerifyEmailForm(request.POST)
        if form.is_valid():
            try:
                dto = VerifyEmailDto(
                    email=form.cleaned_data.get("email"),
                    code=form.cleaned_data.get("code"),
                )
                AuthProvider.verify_email().execute(dto)
                messages.success(
                    request, "Xác minh tài khoản thành công! Bạn hiện có thể đăng nhập."
                )
                return redirect("login")
            except ValueError as e:
                form.add_error(None, str(e))
                messages.error(request, str(e))
    else:
        form = VerifyEmailForm(initial={"email": email})

    return render(
        request,
        "pages/auth/verify_email.html",
        {"form": form, "email": email},
    )
