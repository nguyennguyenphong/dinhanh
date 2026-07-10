from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from accounts.models import PermissionGroup


class PermissionGroupDeleteView(LoginRequiredMixin, View):

    def post(self, request, pk: int):
        group = get_object_or_404(PermissionGroup, id=pk)
        try:
            group.delete()
            messages.success(request, f"Đã xóa nhóm quyền '{group.name}' thành công.")
        except Exception as exc:
            messages.error(request, f"Lỗi xóa nhóm quyền: {str(exc)}")

        return redirect("group_permission_list")
