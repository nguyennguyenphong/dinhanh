"""
DRF API views for Tenant CRUD operations.

Endpoint map (wired in urls/tenant_urls.py):
    POST   /tenants/                -> TenantListView
"""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.views import View

from tenants.application.dtos import TenantCreateDTO
from tenants.exceptions.exception import TenantDomainError
from tenants.policies import TenantPolicy
from tenants.providers import TenantProvider
from tenants.serializers.tenants.tenant_create_serializer import TenantCreateSerializer
from tenants.services.media_service import FileStorageService
from tenants.utils.request_helpers import get_client_ip
from tenants.views.forms import TenantBaseForm
from tenants.views.helpers.view_helpers import RequestContext


class TenantCreateView(LoginRequiredMixin, View):
    """
    Handle Tenant creation:
    1. GET: Render the creation form.
    2. POST: Validate data, process file upload, execute UseCase, and redirect.
    """

    def get(self, request):
        form = TenantBaseForm()
        return render(request, "pages/create.html", {"form": form})

    def post(self, request):
        form = TenantBaseForm(request.POST, request.FILES)

        if form.is_valid():
            # 1. Extract cleaned data
            data = form.cleaned_data.copy()

            # 2. Extract logo file
            logo_file = data.pop("logo_url", None)

            # 3. Prepare serializer data (without logo_url)
            serializer_data = data.copy()

            serializer = TenantCreateSerializer(data=serializer_data)

            if serializer.is_valid():
                validated_data = serializer.validated_data

                # 4. Process file upload if provided
                if logo_file:
                    try:
                        print(f"Processing logo file: {logo_file.name}")
                        logo_url = FileStorageService.save_tenant_logo(logo_file)
                        validated_data["logo_url"] = logo_url
                    except ValidationError as e:
                        form.add_error("logo_url", str(e))
                        messages.error(request, f"logo_url: {str(e)}")
                        return render(request, "pages/create.html", {"form": form})
                    except Exception as e:
                        form.add_error("logo_url", f"Lỗi khi lưu tệp: {str(e)}")
                        messages.error(request, f"Lỗi khi lưu tệp: {str(e)}")
                        return render(request, "pages/create.html", {"form": form})
                else:
                    print("No logo file provided - logo_url will be None")

                # 5. Execute UseCase
                ctx = RequestContext.from_request(request)
                dto = TenantCreateDTO(**validated_data)

                ip_address = get_client_ip(request)
                user_agent = request.META.get("HTTP_USER_AGENT", "")

                try:
                    TenantProvider.create_tenant().execute(
                        dto,
                        actor_id=ctx.actor_id,
                        actor_username=ctx.actor_username,
                        ip_address=ip_address,
                        user_agent=user_agent,
                    )
                    messages.success(request, "Tenant tạo thành công.")
                    return redirect("tenant_list")
                except TenantDomainError as exc:
                    form.add_error(None, str(exc))
                    error_text = str(exc).replace("\n", " ").strip()
                    messages.error(request, error_text)
            else:
                # Map serializer errors back to form
                for field, errors in serializer.errors.items():
                    form.add_error(field, errors)
                    error_msg = f"{field}: {errors[0]}"
                    messages.error(request, error_msg)

        return render(request, "pages/create.html", {"form": form})
