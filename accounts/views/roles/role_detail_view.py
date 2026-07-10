from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views import View

from accounts.models import Role


class RoleDetailView(LoginRequiredMixin, View):

    def get(self, request, pk: int):
        role = get_object_or_404(Role.all_objects, id=pk)

        from tenants.models import Tenant

        tenant = Tenant.objects.filter(pk=role.tenant_id).first()
        tenant_name = tenant.name if tenant else "-"

        return render(
            request,
            "pages/roles/detail.html",
            {"role": role, "tenant_name": tenant_name},
        )
