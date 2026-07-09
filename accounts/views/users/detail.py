from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views import View

from accounts.models import UserAccount


class UserDetailView(LoginRequiredMixin, View):

    def get(self, request, pk: int):
        user = get_object_or_404(UserAccount, id=pk)

        from tenants.models import Tenant

        tenant = Tenant.objects.filter(pk=user.tenant_id).first()
        tenant_name = tenant.name if tenant else "-"

        return render(
            request,
            "pages/user_detail.html",
            {"user": user, "tenant_name": tenant_name},
        )
