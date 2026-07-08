from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from accounts.views.forms.permission_base_form import PermissionBaseForm


class PermissionCreateView(LoginRequiredMixin, View):

    def get(self, request):
        form = PermissionBaseForm()
        return render(request, "pages/permission_create.html", {"form": form})

    def post(self, request):
        form = PermissionBaseForm(request.POST)

        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Tạo quyền mới thành công.")
                return redirect("permission_list")
            except Exception as exc:
                form.add_error(None, str(exc))
                messages.error(request, f"Lỗi tạo quyền: {str(exc)}")

        return render(request, "pages/permission_create.html", {"form": form})
