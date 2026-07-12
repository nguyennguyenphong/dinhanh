from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from accounts.views.forms import PasswordChangeForm


class PasswordChangeView(LoginRequiredMixin, View):

    def get(self, request):
        form = PasswordChangeForm()
        return render(request, "pages/auth/password_change.html", {"form": form})

    def post(self, request):
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            user = request.user
            old_password = form.cleaned_data.get("old_password")
            new_password = form.cleaned_data.get("new_password")

            if not user.check_password(old_password):
                form.add_error("old_password", "Mật khẩu cũ không chính xác.")
                messages.error(request, "Mật khẩu cũ không chính xác.")
            else:
                user.change_password(new_password)
                # Keep the user logged in after password change
                update_session_auth_hash(request, user)
                messages.success(request, "Đổi mật khẩu thành công!")
                return redirect("/")
        return render(request, "pages/auth/password_change.html", {"form": form})
