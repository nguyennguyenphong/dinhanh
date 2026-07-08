from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from accounts.views.forms.user_base_form import UserBaseForm


class UserCreateView(LoginRequiredMixin, View):

    def get(self, request):
        form = UserBaseForm()
        return render(request, "pages/user_create.html", {"form": form})

    def post(self, request):
        form = UserBaseForm(request.POST)

        if form.is_valid():
            try:
                user = form.save(commit=False)
                # Hash the password properly
                user.set_password(form.cleaned_data["password"])
                user.save()
                messages.success(request, "Tạo tài khoản người dùng mới thành công.")
                return redirect("user_list")
            except Exception as exc:
                form.add_error(None, str(exc))
                messages.error(request, f"Lỗi tạo người dùng: {str(exc)}")

        return render(request, "pages/user_create.html", {"form": form})
