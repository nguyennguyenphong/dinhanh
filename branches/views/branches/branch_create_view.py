from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from branches.services.branch_service import BranchService
from branches.views.forms.branch_base_form import BranchBaseForm


class BranchCreateView(LoginRequiredMixin, View):

    def get(self, request):
        form = BranchBaseForm()
        return render(request, "pages/branches/create.html", {"form": form})

    def post(self, request):
        form = BranchBaseForm(request.POST)

        if form.is_valid():
            success = BranchService.create_branch(request, form)
            if success:
                return redirect("branch_list")

        return render(request, "pages/branches/create.html", {"form": form})
