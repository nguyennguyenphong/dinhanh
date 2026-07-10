from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from accounts.models import PermissionGroup
from accounts.views.forms.permission_group_base_form import PermissionGroupBaseForm


class PermissionGroupUpdateView(LoginRequiredMixin, View):

    def get(self, request, pk: int):
        group = get_object_or_404(PermissionGroup, id=pk)
        form = PermissionGroupBaseForm(instance=group)
        return render(
            request,
            "pages/group_permission_create.html",
            {"form": form, "object": group, "is_update": True},
        )

    def post(self, request, pk: int):
        group = get_object_or_404(PermissionGroup, id=pk)
        form = PermissionGroupBaseForm(request.POST, instance=group)

        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Cập nhật nhóm quyền thành công.")
                return redirect("group_permission_list")
            except Exception as exc:
                form.add_error(None, str(exc))
                messages.error(request, f"Lỗi cập nhật nhóm quyền: {str(exc)}")

        return render(
            request,
            "pages/group_permission_create.html",
            {"form": form, "object": group, "is_update": True},
        )
