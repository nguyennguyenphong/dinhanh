from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from accounts.views.forms.permission_group_base_form import PermissionGroupBaseForm


class PermissionGroupCreateView(LoginRequiredMixin, View):

    def get(self, request):
        form = PermissionGroupBaseForm()
        return render(request, "pages/group_permissions/create.html", {"form": form})

    def post(self, request):
        form = PermissionGroupBaseForm(request.POST)

        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Tạo nhóm quyền mới thành công.")
                return redirect("group_permission_list")
            except Exception as exc:
                form.add_error(None, str(exc))
                messages.error(request, f"Lỗi tạo nhóm quyền: {str(exc)}")

        return render(request, "pages/group_permissions/create.html", {"form": form})
