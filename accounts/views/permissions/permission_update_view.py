from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from accounts.models import Permission
from accounts.views.forms.permission_base_form import PermissionBaseForm


class PermissionUpdateView(LoginRequiredMixin, View):

    def get(self, request, pk: int):
        permission = get_object_or_404(Permission, id=pk)
        form = PermissionBaseForm(instance=permission)
        return render(
            request,
            "pages/permissions/create.html",
            {"form": form, "object": permission, "is_update": True},
        )

    def post(self, request, pk: int):
        permission = get_object_or_404(Permission, id=pk)
        form = PermissionBaseForm(request.POST, instance=permission)

        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Cập nhật quyền thành công.")
                return redirect("permission_update", pk=permission.id)
            except Exception as exc:
                form.add_error(None, str(exc))
                messages.error(request, f"Lỗi cập nhật quyền: {str(exc)}")

        return render(
            request,
            "pages/permissions/create.html",
            {"form": form, "object": permission, "is_update": True},
        )
