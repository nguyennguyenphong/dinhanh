from __future__ import annotations

from django.contrib import messages
from django.shortcuts import get_object_or_404

from accounts.application.dtos.roles import RoleCreateDto, RoleUpdateDto
from accounts.models.roles import Role
from accounts.providers.role_provider import RoleProvider
from accounts.serializers.role_serializer import (
    RoleCreateSerializer,
    RoleUpdateSerializer,
)


class RoleService:

    @staticmethod
    def create_role(request, form) -> bool:
        """Validate input form data and execute creation UseCase."""
        form_data = {
            "tenant": (
                form.cleaned_data["tenant"].id
                if form.cleaned_data.get("tenant")
                else None
            ),
            "name": form.cleaned_data.get("name"),
            "slug": form.cleaned_data.get("slug"),
            "description": form.cleaned_data.get("description"),
            "is_active": form.cleaned_data.get("is_active") in [True, "True", 1],
        }

        serializer = RoleCreateSerializer(data=form_data)
        if not serializer.is_valid():
            for field, errs in serializer.errors.items():
                form.add_error(field, errs)
                messages.error(request, f"{field}: {errs[0]}")
            return False

        validated = serializer.validated_data

        try:
            dto = RoleCreateDto(
                tenant_id=validated["tenant"],
                name=validated["name"],
                slug=validated.get("slug") or "",
                description=validated.get("description"),
                is_active=validated["is_active"],
            )
            RoleProvider.create_role().execute(dto)
            messages.success(request, "Tạo vai trò mới thành công.")
            return True
        except ValueError as exc:
            form.add_error(None, str(exc))
            messages.error(request, str(exc))
            return False

    @staticmethod
    def update_role(request, pk: int, form) -> bool:
        """Validate, check changes, and execute update UseCase."""
        role_model = get_object_or_404(Role, id=pk)

        if not form.has_changed():
            messages.info(request, "Dữ liệu không thay đổi.")
            return False

        form_data = {
            "name": form.cleaned_data.get("name"),
            "slug": form.cleaned_data.get("slug"),
            "description": form.cleaned_data.get("description"),
            "is_active": form.cleaned_data.get("is_active") in [True, "True", 1],
        }

        serializer = RoleUpdateSerializer(data=form_data)
        if not serializer.is_valid():
            for field, errs in serializer.errors.items():
                form.add_error(field, errs)
                messages.error(request, f"{field}: {errs[0]}")
            return False

        validated = serializer.validated_data

        try:
            dto = RoleUpdateDto(
                name=validated["name"],
                slug=validated["slug"],
                description=validated.get("description"),
                is_active=validated["is_active"],
            )
            RoleProvider.update_role().execute(role_model.uuid, dto)
            messages.success(request, "Cập nhật thông tin vai trò thành công.")
            return True
        except ValueError as exc:
            form.add_error(None, str(exc))
            messages.error(request, str(exc))
            return False

    @staticmethod
    def soft_delete_role(request, pk: int) -> bool:
        role_model = get_object_or_404(Role, id=pk)
        try:
            success = RoleProvider.soft_delete_role().execute(role_model.uuid)
            if success:
                messages.success(request, "Vô hiệu hóa vai trò thành công.")
            return success
        except Exception as exc:
            messages.error(request, f"Lỗi: {str(exc)}")
            return False

    @staticmethod
    def hard_delete_role(request, pk: int) -> bool:
        role_model = get_object_or_404(Role, id=pk)
        try:
            success = RoleProvider.hard_delete_role().execute(role_model.uuid)
            if success:
                messages.success(request, "Xóa vĩnh viễn vai trò thành công.")
            return success
        except Exception as exc:
            messages.error(request, f"Lỗi: {str(exc)}")
            return False
