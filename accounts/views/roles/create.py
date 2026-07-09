from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from accounts.services.role_service import RoleService
from accounts.views.forms.role_base_form import RoleBaseForm


class RoleCreateView(LoginRequiredMixin, View):

    def get(self, request):
        form = RoleBaseForm()
        return render(request, "pages/role_create.html", {"form": form})

    def post(self, request):
        form = RoleBaseForm(request.POST)

        if form.is_valid():
            success = RoleService.create_role(request, form)
            if success:
                return redirect("role_list")

        return render(request, "pages/role_create.html", {"form": form})
