"""
DRF API views for Tenant CRUD operations.

Endpoint map (wired in urls/tenant_urls.py):
    PATCH  /tenants/<pk>/  — partial update
"""

from __future__ import annotations

import uuid

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from tenants.models import Tenant
from tenants.policies import TenantPolicy
from tenants.services.tenant_action_service import TenantActionService
from tenants.views.forms import TenantBaseForm


class TenantUpdateView(LoginRequiredMixin, View):
    """
    GET    /tenants/<pk>/  - tenant detail
    PATCH  /tenants/<pk>/  — partial update
    """

    def get(self, request, pk: uuid.UUID):
        tenant = get_object_or_404(Tenant, uuid=pk)
        return render(
            request,
            "pages/tenants/update.html",
            {"form": TenantBaseForm(instance=tenant), "object": tenant},
        )

    """
    Django does not support direct patching from HTML forms.
    We map POST to PATCH by calling the patch method.
    """

    def post(self, request, pk: uuid.UUID):
        return self.patch(request, pk)

    def patch(self, request, pk: uuid.UUID):
        tenant = get_object_or_404(Tenant, uuid=pk)
        form = TenantBaseForm(request.POST, request.FILES, instance=tenant)

        if form.is_valid():
            if TenantActionService.update_tenant(request, pk, form):
                messages.success(request, "Cập nhật tenant thành công.")
                return redirect("tenant_list")

        return render(request, "pages/tenants/update.html", {"form": form, "object": tenant})
