"""
DRF API views for Tenant CRUD operations.

Endpoint map (wired in urls/tenant_urls.py):
    POST   /tenants/                -> TenantListView
"""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from tenants.services import TenantService
from tenants.views.forms import TenantBaseForm


class TenantCreateView(LoginRequiredMixin, View):
    """
    Handle Tenant creation:
    1. GET: Render the creation form.
    2. POST: Validate data, process file upload, execute UseCase, and redirect.
    """

    def get(self, request):
        form = TenantBaseForm()
        return render(request, "pages/tenants/create.html", {"form": form})

    def post(self, request):
        form = TenantBaseForm(request.POST, request.FILES)

        if form.is_valid():
            success = TenantService.create_tenant(request, form)

            if success:
                messages.success(request, "Tenant tạo thành công.")
                return redirect("tenant_list")

        return render(request, "pages/tenants/create.html", {"form": form})
