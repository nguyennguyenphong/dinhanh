from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from accounts.models import Role
from accounts.services.role_service import RoleService


class RoleHardDeleteView(LoginRequiredMixin, View):

    def post(self, request, pk: int):
        return self.delete(request, pk)

    def delete(self, request, pk: int):
        role = get_object_or_404(Role.all_objects, id=pk)
        if role.is_system:
            messages.error(request, "Không thể xóa vĩnh viễn vai trò hệ thống.")
            return redirect("role_list")

        RoleService.hard_delete_role(request, pk)
        return redirect("role_list")
