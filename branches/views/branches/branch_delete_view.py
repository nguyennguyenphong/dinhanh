from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from branches.models import Branch
from branches.providers.branch_provider import BranchProvider


class BranchDeleteView(LoginRequiredMixin, View):

    def post(self, request, pk: int):
        branch = get_object_or_404(Branch, id=pk)
        try:
            BranchProvider.delete_branch().execute(branch.id)
            messages.success(request, f"Đã xóa chi nhánh '{branch.name}' thành công.")
        except Exception as exc:
            messages.error(request, f"Lỗi xóa chi nhánh: {str(exc)}")

        return redirect("branch_list")
