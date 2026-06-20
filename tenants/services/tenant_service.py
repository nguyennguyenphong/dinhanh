"""
TenantService — high-level service facade.

Purpose: provides a clean Python API that other Django apps (not views)
can call without knowing about DTOs or repositories. Views should prefer
TenantProvider + use-cases directly; this layer is for inter-app use.
"""

from __future__ import annotations

import uuid
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.http import Http404

from tenants.application.dtos import TenantCreateDTO, TenantUpdateDTO
from tenants.application.dtos import TenantResponseDTO
from tenants.exceptions.exception import TenantDomainError
from tenants.models import Tenant
from tenants.providers import TenantProvider
from tenants.serializers import TenantUpdateSerializer
from tenants.serializers.tenants.tenant_create_serializer import TenantCreateSerializer
from tenants.services.media_service import FileStorageService
from tenants.utils.request_helpers import get_client_ip
from tenants.views.helpers.view_helpers import RequestContext


class TenantService:

    @staticmethod
    def create_tenant(request, form) -> bool:
        """
        Returns True if successful, False if unsuccessful.
        Errors are pushed directly to the form to be displayed on the UI.
        """
        data = form.cleaned_data.copy()
        logo_file = data.pop("logo_url", None)

        # Validate with Serializer
        serializer = TenantCreateSerializer(data=data)
        if not serializer.is_valid():
            for field, errors in serializer.errors.items():
                form.add_error(field, errors)
                messages.error(request, f"{field}: {errors[0]}")
            return False

        validated_data = serializer.validated_data

        # Handle File
        if logo_file:
            try:
                validated_data["logo_url"] = FileStorageService.save_tenant_logo(
                    logo_file
                )
            except (ValidationError, Exception) as e:
                form.add_error("logo_url", str(e))
                messages.error(request, f"Lỗi tệp tin: {str(e)}")
                return False

        # Execute UseCase
        try:
            ctx = RequestContext.from_request(request)
            dto = TenantCreateDTO(**validated_data)

            TenantProvider.create_tenant().execute(
                dto,
                actor_id=ctx.actor_id,
                actor_username=ctx.actor_username,
                ip_address=get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )
            return True
        except Exception as exc:
            form.add_error(None, str(exc))
            messages.error(request, str(exc).replace("\n", " ").strip())
            return False

    @staticmethod
    def update_tenant(request, pk: uuid.UUID, form) -> bool:
        tenant_model = get_object_or_404(Tenant, uuid=pk)
        old_logo_url = tenant_model.logo_url
        data = form.cleaned_data.copy()

        # 1. Xử lý ảnh mới
        logo_file = request.FILES.get("logo_url")
        has_new_logo = logo_file is not None
        new_logo_url = None

        if has_new_logo:
            try:
                new_logo_url = FileStorageService.save_tenant_logo(logo_file)
                data["logo_url"] = new_logo_url
            except Exception as e:
                form.add_error("logo_url", f"Lỗi tệp tin: {str(e)}")
                return False
        else:
            data["logo_url"] = old_logo_url

        # 2. Validate serializer
        serializer = TenantUpdateSerializer(
            data=data, context={"tenant_id": tenant_model.id}
        )
        if not serializer.is_valid():
            for field, errors in serializer.errors.items():
                form.add_error(field, errors)
            return False

        check_data = serializer.validated_data.copy()
        check_data.pop("logo_url", None)

        model_data = {
            k: getattr(tenant_model, k)
            for k in check_data.keys()
            if hasattr(tenant_model, k)
        }

        if not has_new_logo and check_data == model_data:
            messages.info(request, "Không có sự thay đổi dữ liệu.")
            return False

        try:
            ctx = RequestContext.from_request(request)
            dto = TenantUpdateDTO(
                tenant_id=tenant_model.id, **serializer.validated_data
            )

            TenantProvider.update_tenant().execute(
                dto,
                actor_id=ctx.actor_id,
                actor_username=ctx.actor_username,
                ip_address=get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )

            if has_new_logo and old_logo_url:
                FileStorageService.delete_logo(old_logo_url)

            return True
        except TenantDomainError as exc:
            if new_logo_url:
                FileStorageService.delete_logo(new_logo_url)
            form.add_error(None, str(exc))
            return False

    @staticmethod
    def soft_delete_tenant(request, pk: uuid.UUID, form) -> bool:
        """
        Handle (Soft Delete) tenant.
        """
        tenant = get_object_or_404(Tenant.all_objects, uuid=pk)
        try:
            ctx = RequestContext.from_request(request)

            TenantProvider.deactivate_tenant().execute(
                tenant.id,
                actor_id=ctx.actor_id,
                actor_username=ctx.actor_username,
                ip_address=get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )

            return True

        except TenantDomainError as exc:
            form.add_error(None, str(exc))
            messages.error(request, str(exc))
            return False

        except Exception as exc:
            form.add_error(None, "Đã xảy ra lỗi không xác định khi xóa tenant.")
            messages.error(request, "Có lỗi trong quá trình thực hiện.")
            return False

    @staticmethod
    def hard_delete_tenant(request, pk: uuid.UUID, form) -> bool:
        """
        Handle (Hard Delete) tenant.
        """
        tenant = get_object_or_404(Tenant.all_objects, uuid=pk)
        try:
            ctx = RequestContext.from_request(request)
            TenantProvider.hard_delete_tenant().execute(
                tenant.id,
                actor_id=ctx.actor_id,
                actor_username=ctx.actor_username,
                ip_address=get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )
            return True
        except Exception as exc:
            form.add_error(None, str(exc))
            messages.error(request, str(exc))
            return False

        except Exception as exc:
            form.add_error(None, "Đã xảy ra lỗi không xác định khi xóa tenant.")
            messages.error(request, f"Lỗi xóa vĩnh viễn: {str(exc)}")
            return False

    @staticmethod
    def deactivate(tenant_id: int, actor_id: int | None = None) -> TenantResponseDTO:
        return TenantProvider.deactivate_tenant().execute(tenant_id, actor_id=actor_id)

    @staticmethod
    def get_by_uuid(pk: uuid.UUID) -> TenantResponseDTO:
        try:
            return TenantProvider.get_tenant().by_uuid(pk)
        except Exception:
            raise Http404("Tenant không tồn tại")
