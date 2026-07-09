from __future__ import annotations

from django.contrib import messages
from django.shortcuts import get_object_or_404

from accounts.application.dtos.users import UserCreateDto, UserUpdateDto
from accounts.models import UserAccount
from accounts.providers.user_provider import UserProvider
from accounts.serializers.user_serializer import UserCreateSerializer, UserUpdateSerializer


class UserService:

    @staticmethod
    def create_user(request, form) -> bool:
        """Validate input form data and execute creation UseCase."""
        form_data = {
            "tenant": form.cleaned_data["tenant"].id if form.cleaned_data.get("tenant") else None,
            "username": form.cleaned_data.get("username"),
            "email": form.cleaned_data.get("email"),
            "password": form.cleaned_data.get("password"),
            "full_name": form.cleaned_data.get("full_name"),
            "phone": form.cleaned_data.get("phone"),
            "avatar": form.cleaned_data.get("avatar"),
            "is_active": form.cleaned_data.get("is_active") in [True, "True", 1],
        }

        serializer = UserCreateSerializer(data=form_data)
        if not serializer.is_valid():
            for field, errs in serializer.errors.items():
                form.add_error(field, errs)
                messages.error(request, f"{field}: {errs[0]}")
            return False

        validated = serializer.validated_data

        try:
            dto = UserCreateDto(
                tenant_id=validated["tenant"],
                username=validated["username"],
                email=validated["email"],
                password=validated["password"],
                full_name=validated["full_name"],
                phone=validated.get("phone"),
                avatar=validated.get("avatar"),
                is_active=validated["is_active"],
            )
            UserProvider.create_user().execute(dto)
            messages.success(request, "Tạo tài khoản người dùng mới thành công.")
            return True
        except ValueError as exc:
            form.add_error(None, str(exc))
            messages.error(request, str(exc))
            return False

    @staticmethod
    def update_user(request, pk: int, form) -> bool:
        """Validate, check changes, and execute update UseCase."""
        user_model = get_object_or_404(UserAccount, id=pk)

        if not form.has_changed():
            messages.info(request, "Dữ liệu không thay đổi.")
            return False

        form_data = {
            "full_name": form.cleaned_data.get("full_name"),
            "phone": form.cleaned_data.get("phone"),
            "avatar": form.cleaned_data.get("avatar"),
            "is_active": form.cleaned_data.get("is_active") in [True, "True", 1],
        }

        serializer = UserUpdateSerializer(data=form_data)
        if not serializer.is_valid():
            for field, errs in serializer.errors.items():
                form.add_error(field, errs)
                messages.error(request, f"{field}: {errs[0]}")
            return False

        validated = serializer.validated_data

        try:
            new_password = form.cleaned_data.get("password")
            if new_password and new_password.strip():
                from django.contrib.auth.hashers import make_password
                user_model.password = make_password(new_password)
                user_model.save()

            dto = UserUpdateDto(
                full_name=validated["full_name"],
                phone=validated.get("phone"),
                avatar=validated.get("avatar"),
                is_active=validated["is_active"],
            )

            UserProvider.update_user().execute(user_model.uuid, dto)
            messages.success(request, "Cập nhật thông tin tài khoản thành công.")
            return True
        except ValueError as exc:
            form.add_error(None, str(exc))
            messages.error(request, str(exc))
            return False

    @staticmethod
    def soft_delete_user(request, pk: int) -> bool:
        user_model = get_object_or_404(UserAccount, id=pk)
        try:
            success = UserProvider.soft_delete_user().execute(user_model.uuid)
            if success:
                messages.success(request, "Vô hiệu hóa tài khoản người dùng thành công.")
            return success
        except Exception as exc:
            messages.error(request, f"Lỗi: {str(exc)}")
            return False

    @staticmethod
    def hard_delete_user(request, pk: int) -> bool:
        user_model = get_object_or_404(UserAccount, id=pk)
        try:
            success = UserProvider.hard_delete_user().execute(user_model.uuid)
            if success:
                messages.success(request, "Xóa vĩnh viễn tài khoản người dùng thành công.")
            return success
        except Exception as exc:
            messages.error(request, f"Lỗi: {str(exc)}")
            return False
