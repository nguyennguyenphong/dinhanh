"""
DRF API views for Tenant CRUD operations.

Endpoint map (wired in urls/tenant_urls.py):
    GET    /tenants/<pk>/           -> TenantDetailView
"""

from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View
import uuid
from django import forms
from django.shortcuts import get_object_or_404
from django.contrib import messages

from tenants.policies import TenantPolicy
from tenants.services import TenantActionService
from tenants.models import Tenant


class TenantSoftDeleteView(LoginRequiredMixin, View):

    """
    Django does not support direct patching from HTML forms.
    We map POST to DELETE by calling the patch method.
    """
    def post(self, request, pk: uuid.UUID):
        return self.delete(request, pk)
    
    def delete(self, request, pk: uuid.UUID):
        form = forms.Form(request.POST)
        
        if TenantActionService.soft_delete_tenant(request, pk, form):
            messages.success(request, "Đã xóa tạm thời tenant.")
        else:
            pass
        
        return redirect("tenant_list")