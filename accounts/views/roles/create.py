from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from accounts.views.forms.role_base_form import RoleBaseForm


class RoleCreateView(LoginRequiredMixin, View):

    def get(self, request):
        form = RoleBaseForm()
        return render(request, "pages/role_create.html", {"form": form})

    def post(self, request):
        form = RoleBaseForm(request.POST)

        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Tạo vai trò mới thành công.")
                return redirect("role_list")
            except Exception as exc:
                form.add_error(None, str(exc))
                messages.error(request, f"Lỗi tạo vai trò: {str(exc)}")

        return render(request, "pages/role_create.html", {"form": form})
