from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from branches.models import Branch
from branches.providers.branch_provider import BranchProvider


class BranchHardDeleteView(LoginRequiredMixin, View):

    def post(self, request, pk: int):
        # Fetching with all_objects since it might be soft deleted first
        branch = get_object_or_404(Branch.all_objects, id=pk)
        try:
            BranchProvider.hard_delete_branch().execute(
                branch.id,
                actor_id=request.user.id if request.user else None,
                actor_username=request.user.username if request.user else None,
            )
            messages.success(
                request, f"Đã xóa vĩnh viễn chi nhánh '{branch.name}' thành công."
            )
        except Exception as exc:
            messages.error(request, f"Lỗi xóa vĩnh viễn chi nhánh: {str(exc)}")

        return redirect("branch_list")
