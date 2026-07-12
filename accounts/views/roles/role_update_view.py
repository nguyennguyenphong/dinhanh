from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from accounts.models import Role
from accounts.services.role_service import RoleService
from accounts.views.forms.role_base_form import RoleBaseForm


class RoleUpdateView(LoginRequiredMixin, View):

    def get(self, request, pk: int):
        role = get_object_or_404(Role, id=pk)
        form = RoleBaseForm(instance=role)
        return render(
            request,
            "pages/roles/create.html",
            {"form": form, "object": role, "is_update": True},
        )

    def post(self, request, pk: int):
        return self.patch(request, pk)

    def patch(self, request, pk: int):
        role = get_object_or_404(Role, id=pk)
        form = RoleBaseForm(request.POST, instance=role)

        if form.is_valid():
            success = RoleService.update_role(request, pk, form)
            if success:
                return redirect("role_update", pk=role.id)

        return render(
            request,
            "pages/roles/create.html",
            {"form": form, "object": role, "is_update": True},
        )
