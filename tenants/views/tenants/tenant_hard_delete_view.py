"""
DRF API views for Tenant CRUD operations.

Endpoint map (wired in urls/tenant_urls.py):
    DELETE /tenants/<pk>/           -> TenantDetailView  (soft deactivate)
    DELETE /tenants/<pk>/hard/      -> TenantHardDeleteView (superuser only)
"""

from __future__ import annotations

import uuid

from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from tenants.models import Tenant
from tenants.policies import TenantPolicy
from tenants.services import TenantService


class TenantHardDeleteView(LoginRequiredMixin, View):
    """
    DELETE /tenants/<pk>/hard/  — permanent delete (superuser only)
    """

    """
    Django does not support direct patching from HTML forms.
    We map POST to DELETE by calling the patch method.
    """

    def post(self, request, pk: uuid.UUID):
        return self.delete(request, pk)

    def delete(self, request, pk: uuid.UUID):
        tenant = get_object_or_404(Tenant.all_objects, uuid=pk)
        form = forms.Form(request.POST)

        if TenantService.hard_delete_tenant(request, pk, form):
            messages.success(request, f"Đã xóa vĩnh viễn tenant '{tenant.name}'.")

        return redirect("tenant_list")
