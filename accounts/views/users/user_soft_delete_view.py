from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from accounts.models import UserAccount
from accounts.services.user_service import UserService


class UserSoftDeleteView(LoginRequiredMixin, View):
    """
    Handle user soft deletion: deactivates the user account (is_active = False).
    """

    def post(self, request, pk: int):
        return self.delete(request, pk)

    def delete(self, request, pk: int):
        user = get_object_or_404(UserAccount, id=pk)
        if user == request.user:
            messages.error(
                request, "Không thể tự vô hiệu hóa tài khoản của chính mình."
            )
            return redirect("user_list")

        UserService.soft_delete_user(request, pk)
        return redirect("user_list")
