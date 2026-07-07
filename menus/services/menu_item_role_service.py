from __future__ import annotations

import uuid
from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404

from menus.application.dtos.menu_item_roles import (
    MenuItemRoleCreateDto,
    MenuItemRoleResponseDto,
    MenuItemRoleDeleteDto,
)
from menus.models.menu_item_roles import MenuItemRole
from menus.providers.menu_item_role_provider import MenuItemRoleProvider
from menus.serializers.menu_item_roles import (
    MenuItemRoleCreateSerializer,
)


class MenuItemRoleService:
    """Service layer coordinating requests/forms validation and UseCases execution for MenuItemRole."""

    @staticmethod
    def get_menu_item_role_detail(request, pk: uuid.UUID) -> bool:
        menu_item_role = get_object_or_404(MenuItemRole, uuid=pk)
        if menu_item_role:
            MenuItemRoleProvider.get_menu_item_role_detail().execute(menu_item_role.id)
            return True
        else:
            messages.error(request, "Menu item role assignment not found.")
            return False

    @staticmethod
    def create_menu_item_role(request, form) -> bool:
        data = form.cleaned_data.copy()

        # Handle foreign key objects mapping to ID
        menu_item_obj = data.get("menu_item")
        if menu_item_obj and hasattr(menu_item_obj, "pk"):
            data["menu_item"] = menu_item_obj.pk

        role_obj = data.get("role")
        if role_obj and hasattr(role_obj, "pk"):
            data["role"] = role_obj.pk

        serializer = MenuItemRoleCreateSerializer(data=data)

        if not serializer.is_valid():
            for field, errors in serializer.errors.items():
                clean_errors = [str(err) for err in errors]
                target_field = field if field in form.fields else None
                form.add_error(target_field, clean_errors)
                messages.error(request, f"{field}: {clean_errors[0]}")
            return False

        validated_data = serializer.validated_data

        try:
            dto = MenuItemRoleCreateDto(
                menu_item_id=validated_data["menu_item"],
                role_id=validated_data["role"],
            )
            MenuItemRoleProvider.create_menu_item_role().execute(dto)
            return True
        except Exception as exc:
            form.add_error(None, str(exc))
            messages.error(request, str(exc).replace("\n", " ").strip())
            return False

    @staticmethod
    def delete_menu_item_role(request, pk: uuid.UUID, form) -> bool:
        menu_item_role = get_object_or_404(MenuItemRole, uuid=pk)
        try:
            dto = MenuItemRoleDeleteDto(
                id=menu_item_role.id,
                tenant_id=menu_item_role.menu_item.tenant_id,
            )
            MenuItemRoleProvider.delete_menu_item_role().execute(dto)
            return True
        except Exception as exc:
            form.add_error(None, str(exc))
            messages.error(request, str(exc))
            return False

    @staticmethod
    def hard_delete_menu_item_role(request, pk: uuid.UUID, form) -> bool:
        menu_item_role = get_object_or_404(MenuItemRole, uuid=pk)
        try:
            dto = MenuItemRoleDeleteDto(
                id=menu_item_role.id,
                tenant_id=menu_item_role.menu_item.tenant_id,
            )
            MenuItemRoleProvider.hard_delete_menu_item_role().execute(dto)
            return True
        except Exception as exc:
            form.add_error(None, str(exc))
            messages.error(request, str(exc))
            return False

    @staticmethod
    def get_by_uuid(pk: uuid.UUID) -> MenuItemRoleResponseDto:
        menu_item_role = get_object_or_404(MenuItemRole, uuid=pk)
        try:
            return MenuItemRoleProvider.get_menu_item_role_detail().execute(menu_item_role.id)
        except Exception:
            raise Http404("Menu item role assignment does not exist.")
