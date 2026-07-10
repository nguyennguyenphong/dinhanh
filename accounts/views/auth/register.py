from django.contrib import messages
from django.shortcuts import redirect, render

from accounts.application.dtos.auth.auth_dto import RegisterDto
from accounts.providers.auth.auth_provider import AuthProvider
from accounts.views.forms import RegisterBaseForm


def register(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        form = RegisterBaseForm(request.POST)
        if form.is_valid():
            try:
                dto = RegisterDto(
                    username=form.cleaned_data.get("username"),
                    email=form.cleaned_data.get("email"),
                    password=form.cleaned_data.get("password"),
                    full_name=form.cleaned_data.get(
                        "username"
                    ),  # default full_name to username
                )
                AuthProvider.register_user().execute(dto)
                messages.success(
                    request,
                    "Đăng ký tài khoản thành công! Vui lòng nhập mã xác thực OTP gửi đến email của bạn.",
                )
                return redirect(f"/accounts/verify_email/?email={dto.email}")
            except ValueError as e:
                form.add_error(None, str(e))
                messages.error(request, str(e))
    else:
        form = RegisterBaseForm()

    return render(request, "pages/auth/register.html", {"form": form})
