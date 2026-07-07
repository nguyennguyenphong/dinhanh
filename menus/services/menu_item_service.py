from __future__ import annotations

import uuid

from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404

from menus.application.dtos.menu_items import (
    MenuItemCreateDto,
    MenuItemDeleteDto,
    MenuItemResponseDto,
    MenuItemUpdateDto,
)
from menus.exceptions import MenuItemDomainError
from menus.models.menu_items import MenuItem
from menus.providers.menu_item_provider import MenuItemProvider
from menus.serializers.menu_items import (
    MenuItemCreateSerializer,
    MenuItemUpdateSerializer,
)
from menus.views.helpers.view_helpers import RequestContext


class MenuItemService:
    """Service layer coordinating requests/forms validation and UseCases execution for MenuItem."""

    @staticmethod
    def get_menu_item_detail(request, pk: uuid.UUID) -> bool:
        """Fetch menu item details by UUID and verify existence."""
        menu_item = get_object_or_404(MenuItem.all_objects, uuid=pk)
        if menu_item:
            MenuItemProvider.get_menu_item_detail().execute(menu_item.id)
            return True
        else:
            messages.error(request, "Menu item not found.")
            return False

    @staticmethod
    def create_menu_item(request, form) -> bool:
        """Validate input form data with serializer and execute creation UseCase."""
        data = form.cleaned_data.copy()

        tenant_obj = data.get("tenant")
        if tenant_obj and hasattr(tenant_obj, "pk"):
            data["tenant"] = tenant_obj.pk

        group_obj = data.get("group")
        if group_obj and hasattr(group_obj, "pk"):
            data["group_id"] = group_obj.pk
        elif "group" in data:
            data["group_id"] = data.pop("group")

        parent_obj = data.get("parent")
        if parent_obj and hasattr(parent_obj, "pk"):
            data["parent_id"] = parent_obj.pk
        elif "parent" in data:
            data["parent_id"] = data.pop("parent")

        repo_instance = MenuItemProvider._menu_item_repo()

        serializer = MenuItemCreateSerializer(
            data=data, context={"menu_item_repo": repo_instance}
        )

        if not serializer.is_valid():
            for field, errors in serializer.errors.items():
                clean_errors = [str(err) for err in errors]
                target_field = field if field in form.fields else None
                form.add_error(target_field, clean_errors)
                messages.error(request, f"{field}: {clean_errors[0]}")
            return False

        validated_data = serializer.validated_data

        try:
            dto = MenuItemCreateDto(**validated_data)
            MenuItemProvider.create_menu_item().execute(dto)
            return True
        except Exception as exc:
            form.add_error(None, str(exc))
            messages.error(request, str(exc).replace("\n", " ").strip())
            return False

    @staticmethod
    def update_menu_item(request, pk: uuid.UUID, form) -> bool:
        """Validate input form data with serializer and execute update UseCase."""
        menu_item_model = get_object_or_404(MenuItem, uuid=pk)

        data = form.cleaned_data.copy()
        data["id"] = menu_item_model.id
        data["uuid"] = menu_item_model.uuid

        group_obj = data.get("group")
        if group_obj and hasattr(group_obj, "pk"):
            data["group_id"] = group_obj.pk
        elif "group" in data:
            data["group_id"] = data.pop("group")

        parent_obj = data.get("parent")
        if parent_obj and hasattr(parent_obj, "pk"):
            data["parent_id"] = parent_obj.pk
        elif "parent" in data:
            data["parent_id"] = data.pop("parent")

        repo_instance = MenuItemProvider._menu_item_repo()

        serializer = MenuItemUpdateSerializer(
            data=data, context={"menu_item_repo": repo_instance}
        )
        if not serializer.is_valid():
            for field, errors in serializer.errors.items():
                form.add_error(field, errors)
            return False

        try:
            RequestContext.from_request(request)
            dto = MenuItemUpdateDto(**serializer.validated_data)

            MenuItemProvider.update_menu_item().execute(dto)
            return True
        except MenuItemDomainError as exc:
            form.add_error(None, str(exc))
            return False

    @staticmethod
    def delete_menu_item(request, pk: uuid.UUID, form) -> bool:
        """Soft delete MenuItem using DeleteMenuItemUseCase."""
        menu_item = get_object_or_404(MenuItem.all_objects, uuid=pk)
        try:
            RequestContext.from_request(request)
            dto = MenuItemDeleteDto(
                id=menu_item.id,
                tenant_id=menu_item.tenant_id,
            )
            MenuItemProvider.delete_menu_item().execute(dto)
            return True
        except MenuItemDomainError as exc:
            form.add_error(None, str(exc))
            messages.error(request, str(exc))
            return False
        except Exception:
            form.add_error(None, "Unknown error occurred while deleting menu item.")
            messages.error(request, "An error occurred during deletion.")
            return False

    @staticmethod
    def hard_delete_menu_item(request, pk: uuid.UUID, form) -> bool:
        """Hard delete MenuItem using HardDeleteMenuItemUseCase."""
        menu_item = get_object_or_404(MenuItem.all_objects, uuid=pk)
        try:
            RequestContext.from_request(request)
            dto = MenuItemDeleteDto(
                id=menu_item.id,
                tenant_id=menu_item.tenant_id,
            )
            MenuItemProvider.hard_delete_menu_item().execute(dto)
            return True
        except Exception as exc:
            form.add_error(None, str(exc))
            messages.error(request, str(exc))
            return False

    @staticmethod
    def get_by_uuid(pk: uuid.UUID) -> MenuItemResponseDto:
        """Get flat response DTO by UUID."""
        menu_item = get_object_or_404(MenuItem.all_objects, uuid=pk)
        try:
            return MenuItemProvider.get_menu_item_detail().execute(menu_item.id)
        except Exception:
            raise Http404("Menu item does not exist.")
