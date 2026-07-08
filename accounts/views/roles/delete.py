from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from accounts.models import Role


class RoleDeleteView(LoginRequiredMixin, View):

    def post(self, request, pk: int):
        role = get_object_or_404(Role, id=pk)
        if role.is_system:
            messages.error(request, "Không thể xóa vai trò hệ thống mặc định.")
            return redirect("role_list")

        try:
            role.delete()
            messages.success(request, f"Đã xóa vai trò '{role.name}' thành công.")
        except Exception as exc:
            messages.error(request, f"Lỗi xóa vai trò: {str(exc)}")

        return redirect("role_list")
