from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from branches.views.forms import BranchBaseForm


class BranchUpdateView(LoginRequiredMixin, View):

    def get(self, request):
        form = BranchBaseForm()
        return render(request, "pages/branches/update.html", {"form": form})
