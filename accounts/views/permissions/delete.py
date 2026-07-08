from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from accounts.models import Permission


class PermissionDeleteView(LoginRequiredMixin, View):

    def post(self, request, pk: int):
        permission = get_object_or_404(Permission, id=pk)
        if permission.is_system:
            messages.error(request, "Không thể xóa quyền hệ thống mặc định.")
            return redirect("permission_list")

        try:
            permission.delete()
            messages.success(
                request, f"Đã xóa quyền '{permission.codename}' thành công."
            )
        except Exception as exc:
            messages.error(request, f"Lỗi xóa quyền: {str(exc)}")

        return redirect("permission_list")
