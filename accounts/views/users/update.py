from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from accounts.models import UserAccount
from accounts.views.forms.user_base_form import UserBaseForm


class UserUpdateView(LoginRequiredMixin, View):

    def get(self, request, pk: int):
        user = get_object_or_404(UserAccount, id=pk)
        form = UserBaseForm(instance=user)
        return render(
            request,
            "pages/user_create.html",
            {"form": form, "object": user, "is_update": True},
        )

    def post(self, request, pk: int):
        user = get_object_or_404(UserAccount, id=pk)
        form = UserBaseForm(request.POST, instance=user)

        if form.is_valid():
            try:
                updated_user = form.save(commit=False)
                new_pw = form.cleaned_data.get("password")
                if new_pw:
                    updated_user.set_password(new_pw)
                updated_user.save()
                messages.success(request, "Cập nhật thông tin tài khoản thành công.")
                return redirect("user_list")
            except Exception as exc:
                form.add_error(None, str(exc))
                messages.error(request, f"Lỗi cập nhật thông tin: {str(exc)}")

        return render(
            request,
            "pages/user_create.html",
            {"form": form, "object": user, "is_update": True},
        )
