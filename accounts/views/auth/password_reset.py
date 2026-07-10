from django.contrib import messages
from django.shortcuts import redirect, render

from accounts.application.dtos.auth.auth_dto import ForgotPasswordDto
from accounts.providers.auth.auth_provider import AuthProvider
from accounts.views.forms import ForgotPasswordForm


def password_reset(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            try:
                dto = ForgotPasswordDto(email=form.cleaned_data.get("email"))
                AuthProvider.forgot_password().execute(dto)
                messages.success(
                    request,
                    "Mã OTP khôi phục mật khẩu đã được gửi đến email của bạn.",
                )
                return redirect(f"/accounts/password_reset_confirm/?email={dto.email}")
            except ValueError as e:
                form.add_error(None, str(e))
                messages.error(request, str(e))
    else:
        form = ForgotPasswordForm()

    return render(request, "pages/auth/password_reset.html", {"form": form})
