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

from tenants.application.dtos import TenantCreateDTO
from tenants.exceptions.exception import TenantDomainError
from tenants.policies import TenantPolicy
from tenants.providers import TenantProvider
from tenants.serializers.tenants.tenant_create_serializer import TenantCreateSerializer
from tenants.views.forms import TenantCreateForm
from tenants.views.helpers.view_helpers import RequestContext


class TenantCreateView(LoginRequiredMixin, View):
    """
    Handle Tenant creation:
    1. GET: Render the creation form.
    2. POST: Process form data, execute UseCase, and redirect.
    """

    def get(self, request):
        form = TenantCreateForm()
        return render(request, "pages/create.html", {"form": form})

    def post(self, request):
        # 1. Extract data from request.POST (or use Django Forms for better validation)
        form = TenantCreateForm(request.POST)
        if form.is_valid():
            serializer = TenantCreateSerializer(data=form.cleaned_data)

            if serializer.is_valid():
                ctx = RequestContext.from_request(request)
                dto = TenantCreateDTO(**serializer.validated_data)

                try:
                    TenantProvider.create_tenant().execute(
                        dto,
                        actor_id=ctx.actor_id,
                        actor_username=ctx.actor_username,
                    )
                    messages.success(request, "Tenant created successfully.")
                    return redirect("tenant_list")
                except TenantDomainError as exc:
                    form.add_error(None, str(exc))
            else:
                for field, errors in serializer.errors.items():
                    form.add_error(field, errors)

        return render(request, "pages/create.html", {"form": form})
