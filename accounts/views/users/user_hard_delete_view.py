from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from accounts.models import UserAccount
from accounts.services.user_service import UserService


class UserHardDeleteView(LoginRequiredMixin, View):
    """
    Handle user hard deletion: permanently purges the user from the database.
    """

    def post(self, request, pk: int):
        return self.delete(request, pk)

    def delete(self, request, pk: int):
        user = get_object_or_404(UserAccount, id=pk)
        if user == request.user:
            messages.error(request, "Không thể tự xóa vĩnh viễn tài khoản của chính mình.")
            return redirect("user_list")

        UserService.hard_delete_user(request, pk)
        return redirect("user_list")
