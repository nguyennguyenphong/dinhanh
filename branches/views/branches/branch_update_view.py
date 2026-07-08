from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from branches.models import Branch
from branches.services.branch_service import BranchService
from branches.views.forms.branch_base_form import BranchBaseForm


class BranchUpdateView(LoginRequiredMixin, View):

    def get(self, request, pk: int):
        branch = get_object_or_404(Branch, id=pk)
        form = BranchBaseForm(instance=branch)
        return render(
            request,
            "pages/branches/update.html",
            {"form": form, "object": branch},
        )

    def post(self, request, pk: int):
        branch = get_object_or_404(Branch, id=pk)
        form = BranchBaseForm(request.POST, instance=branch)

        if form.is_valid():
            success = BranchService.update_branch(request, pk, form)
            if success:
                return redirect("branch_list")

        return render(
            request,
            "pages/branches/update.html",
            {"form": form, "object": branch},
        )
