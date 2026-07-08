from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views import View

from branches.models import Branch
from branches.providers.branch_provider import BranchProvider


class BranchDetailView(LoginRequiredMixin, View):

    def get(self, request, pk: int):
        branch = get_object_or_404(Branch, id=pk)
        branch_dto = BranchProvider.get_branch().execute(branch.id)
        return render(
            request,
            "pages/branches/detail.html",
            {"branch": branch_dto, "object": branch},
        )
