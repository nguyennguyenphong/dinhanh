from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from accounts.models import UserAccount


class UserDeleteView(LoginRequiredMixin, View):

    def post(self, request, pk: int):
        user = get_object_or_404(UserAccount, id=pk)
        if user == request.user:
            messages.error(request, "Không thể tự xóa chính tài khoản đang đăng nhập.")
            return redirect("user_list")

        try:
            user.delete()
            messages.success(request, f"Đã xóa tài khoản '{user.username}' thành công.")
        except Exception as exc:
            messages.error(request, f"Lỗi xóa tài khoản: {str(exc)}")

        return redirect("user_list")
