"""
DRF API views for Tenant CRUD operations.

Endpoint map (wired in urls/tenant_urls.py):
    GET    /tenants/<pk>/           -> TenantDetailView
"""

from __future__ import annotations

import uuid

from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View

from tenants.services import TenantService


class TenantSoftDeleteView(LoginRequiredMixin, View):
    """
    Django does not support direct patching from HTML forms.
    We map POST to DELETE by calling the patch method.
    """

    def post(self, request, pk: uuid.UUID):
        return self.delete(request, pk)

    def delete(self, request, pk: uuid.UUID):
        form = forms.Form(request.POST)

        if TenantService.soft_delete_tenant(request, pk, form):
            messages.success(request, "Đã xóa tạm thời tenant.")
        else:
            pass

        return redirect("tenant_list")
