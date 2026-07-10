from django.contrib import messages
from django.shortcuts import redirect, render

from accounts.application.dtos.auth.auth_dto import ConfirmPasswordResetDto
from accounts.providers.auth.auth_provider import AuthProvider
from accounts.views.forms import ConfirmPasswordResetForm


def password_reset_confirm(request):
    if request.user.is_authenticated:
        return redirect("/")

    email = request.GET.get("email", "")

    if request.method == "POST":
        form = ConfirmPasswordResetForm(request.POST)
        if form.is_valid():
            try:
                dto = ConfirmPasswordResetDto(
                    email=form.cleaned_data.get("email"),
                    code=form.cleaned_data.get("code"),
                    new_password=form.cleaned_data.get("new_password"),
                )
                AuthProvider.confirm_password_reset().execute(dto)
                messages.success(
                    request,
                    "Mật khẩu của bạn đã được thay đổi thành công! Vui lòng đăng nhập lại.",
                )
                return redirect("password_reset_complete")
            except ValueError as e:
                form.add_error(None, str(e))
                messages.error(request, str(e))
    else:
        form = ConfirmPasswordResetForm(initial={"email": email})

    return render(
        request,
        "pages/auth/password_reset_confirm.html",
        {"form": form, "email": email},
    )
