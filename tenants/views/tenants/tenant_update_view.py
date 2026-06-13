"""
DRF API views for Tenant CRUD operations.

Endpoint map (wired in urls/tenant_urls.py):
    PATCH  /tenants/<pk>/  — partial update
"""

from __future__ import annotations

import uuid

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views import View

from tenants.application.dtos import TenantUpdateDTO
from tenants.exceptions.exception import TenantDomainError
from tenants.models import Tenant
from tenants.policies import TenantPolicy
from tenants.providers import TenantProvider
from tenants.serializers import (
    TenantUpdateSerializer,
)
from tenants.services.media_service import FileStorageService
from tenants.utils.request_helpers import get_client_ip
from tenants.views.forms import TenantBaseForm
from tenants.views.helpers.view_helpers import RequestContext, domain_error_response


class TenantUpdateView(LoginRequiredMixin, View):
    """
    GET    /tenants/<pk>/  - tenant detail
    PATCH  /tenants/<pk>/  — partial update
    """

    def get(self, request, pk: uuid.UUID):
        try:
            tenant = TenantProvider.get_tenant().by_uuid(pk)
        except Exception:
            raise Http404("Tenant không tồn tại")

        tenant_model = get_object_or_404(Tenant, uuid=pk)

        form = TenantBaseForm(instance=tenant_model)

        return render(request, "pages/update.html", {"form": form, "object": tenant})

    """
    Django does not support direct patching from HTML forms.
    We map POST to PATCH by calling the patch method.
    """

    def post(self, request, pk: uuid.UUID):
        return self.patch(request, pk)

    def patch(self, request, pk: uuid.UUID):
        tenant_model = get_object_or_404(Tenant, uuid=pk)

        form = TenantBaseForm(request.POST, request.FILES, instance=tenant_model)

        if form.is_valid():
            logo_file = request.FILES.get("logo_url")
            cleaned_data = form.cleaned_data.copy()

            logo_file = cleaned_data.pop("logo_url", None)

            serializer = TenantUpdateSerializer(
                data=cleaned_data, context={"tenant_id": tenant_model.id}
            )

            if serializer.is_valid():
                if logo_file:
                    try:
                        logo_url = FileStorageService.save_tenant_logo(logo_file)
                        cleaned_data["logo_url"] = logo_url
                    except Exception as e:
                        messages.error(request, f"Lỗi khi lưu ảnh: {str(e)}")
                        return render(
                            request,
                            "pages/update.html",
                            {"form": form, "object": tenant_model},
                        )
                else:
                    cleaned_data["logo_url"] = tenant_model.logo_url

                tenant_id = tenant_model.id

                dto = TenantUpdateDTO(tenant_id=tenant_id, **cleaned_data)

                ctx = RequestContext.from_request(request)
                try:
                    TenantProvider.update_tenant().execute(
                        dto,
                        actor_id=ctx.actor_id,
                        actor_username=ctx.actor_username,
                        ip_address=get_client_ip(request),
                        user_agent=request.META.get("HTTP_USER_AGENT", ""),
                    )
                    messages.success(request, "Cập nhật tenant thành công.")
                except TenantDomainError as exc:
                    form.add_error(None, str(exc))
                    error_text = str(exc).replace("\n", " ").strip()
                    messages.error(request, error_text)

            else:
                for field, errors in serializer.errors.items():
                    form.add_error(field, errors)
                    error_msg = f"{field}: {errors[0]}"
                    messages.error(request, error_msg)

        return render(
            request, "pages/update.html", {"form": form, "object": form.instance}
        )
