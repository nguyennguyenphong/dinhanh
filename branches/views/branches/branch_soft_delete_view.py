from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from branches.models import Branch
from branches.providers.branch_provider import BranchProvider


class BranchSoftDeleteView(LoginRequiredMixin, View):

    def post(self, request, pk: int):
        branch = get_object_or_404(Branch, id=pk)
        try:
            BranchProvider.soft_delete_branch().execute(
                branch.id,
                actor_id=request.user.id if request.user else None,
                actor_username=request.user.username if request.user else None,
            )
            messages.success(
                request, f"Đã xóa tạm thời chi nhánh '{branch.name}' thành công."
            )
        except Exception as exc:
            messages.error(request, f"Lỗi xóa tạm thời chi nhánh: {str(exc)}")

        return redirect("branch_list")
