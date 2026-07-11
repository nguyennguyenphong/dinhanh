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

        # Check sort_order collision
        target_sort = validated_data.get("sort_order", 0)
        if MenuItem.objects.filter(
            tenant_id=validated_data["tenant"], sort_order=target_sort
        ).exists():
            err_msg = f"Thứ tự hiển thị {target_sort} đã tồn tại."
            form.add_error("sort_order", err_msg)
            messages.error(request, err_msg)
            return False

        try:
            dto = MenuItemCreateDto(**validated_data)
            MenuItemProvider.create_menu_item().execute(dto)

            # Log MenuItem creation
            from menus.models.menu_audit_log import MenuAuditLog

            MenuAuditLog.objects.create(
                tenant_id=validated_data["tenant"],
                action="CREATE",
                actor_id=request.user.id if request.user.is_authenticated else None,
                new_values={
                    "code": validated_data.get("code"),
                    "label": validated_data.get("label"),
                    "url_path": validated_data.get("url_path"),
                    "sort_order": validated_data.get("sort_order"),
                    "is_active": validated_data.get("is_active"),
                },
            )
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

        check_data = {
            "code": serializer.validated_data.get("code"),
            "label": serializer.validated_data.get("label"),
            "group_id": serializer.validated_data.get("group_id"),
            "parent_id": serializer.validated_data.get("parent_id"),
            "url_name": serializer.validated_data.get("url_name"),
            "url_path": serializer.validated_data.get("url_path"),
            "icon": serializer.validated_data.get("icon"),
            "badge": serializer.validated_data.get("badge"),
            "permission_code": serializer.validated_data.get("permission_code"),
            "sort_order": serializer.validated_data.get("sort_order"),
            "open_in_new_tab": serializer.validated_data.get("open_in_new_tab"),
            "is_active": serializer.validated_data.get("is_active"),
            "is_hidden": serializer.validated_data.get("is_hidden"),
        }
        model_data = {
            "code": menu_item_model.code,
            "label": menu_item_model.label,
            "group_id": menu_item_model.group_id,
            "parent_id": menu_item_model.parent_id,
            "url_name": menu_item_model.url_name,
            "url_path": menu_item_model.url_path,
            "icon": menu_item_model.icon,
            "badge": menu_item_model.badge_text,
            "permission_code": menu_item_model.permission_code,
            "sort_order": menu_item_model.sort_order,
            "open_in_new_tab": menu_item_model.open_in_new_tab,
            "is_active": menu_item_model.is_active,
            "is_hidden": menu_item_model.is_hidden,
        }
        if check_data == model_data:
            messages.info(request, "Dữ liệu không thay đổi.")
            return False

        # Check sort_order collision
        target_sort = serializer.validated_data.get("sort_order", 0)
        qs = MenuItem.objects.filter(
            tenant_id=menu_item_model.tenant_id, sort_order=target_sort
        )
        if qs.exclude(pk=menu_item_model.pk).exists():
            err_msg = f"Thứ tự hiển thị {target_sort} đã tồn tại."
            form.add_error("sort_order", err_msg)
            messages.error(request, err_msg)
            return False

        try:
            from menus.views.helpers.view_helpers import RequestContext
            RequestContext.from_request(request)
            dto = MenuItemUpdateDto(**serializer.validated_data)

            # Capture old state before update
            old_values = {
                "code": menu_item_model.code,
                "label": menu_item_model.label,
                "url_path": menu_item_model.url_path,
                "sort_order": menu_item_model.sort_order,
                "is_active": menu_item_model.is_active,
            }

            MenuItemProvider.update_menu_item().execute(dto)

            # Log MenuItem update
            from menus.models.menu_audit_log import MenuAuditLog

            MenuAuditLog.objects.create(
                tenant_id=menu_item_model.tenant_id,
                action="UPDATE",
                actor_id=request.user.id if request.user.is_authenticated else None,
                old_values=old_values,
                new_values={
                    "code": serializer.validated_data.get("code"),
                    "label": serializer.validated_data.get("label"),
                    "url_path": serializer.validated_data.get("url_path"),
                    "sort_order": serializer.validated_data.get("sort_order"),
                    "is_active": serializer.validated_data.get("is_active"),
                },
            )
            return True
        except (MenuItemDomainError, ValueError) as exc:
            form.add_error(None, str(exc))
            messages.error(request, str(exc))
            return False

    @staticmethod
    def delete_menu_item(request, pk: uuid.UUID, form) -> bool:
        """Soft delete MenuItem using DeleteMenuItemUseCase."""
        menu_item = get_object_or_404(MenuItem.all_objects, uuid=pk)
        try:
            from menus.views.helpers.view_helpers import RequestContext
            RequestContext.from_request(request)
            dto = MenuItemDeleteDto(
                id=menu_item.id,
                tenant_id=menu_item.tenant_id,
            )
            MenuItemProvider.delete_menu_item().execute(dto)

            # Log MenuItem soft delete
            from menus.models.menu_audit_log import MenuAuditLog

            MenuAuditLog.objects.create(
                tenant_id=menu_item.tenant_id,
                action="DELETE",
                actor_id=request.user.id if request.user.is_authenticated else None,
                old_values={
                    "code": menu_item.code,
                    "label": menu_item.label,
                    "is_active": menu_item.is_active,
                },
            )
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
            from menus.views.helpers.view_helpers import RequestContext
            RequestContext.from_request(request)
            dto = MenuItemDeleteDto(
                id=menu_item.id,
                tenant_id=menu_item.tenant_id,
            )
            MenuItemProvider.hard_delete_menu_item().execute(dto)

            # Log MenuItem hard delete
            from menus.models.menu_audit_log import MenuAuditLog

            MenuAuditLog.objects.create(
                tenant_id=menu_item.tenant_id,
                action="DELETE",
                actor_id=request.user.id if request.user.is_authenticated else None,
                old_values={
                    "code": menu_item.code,
                    "label": menu_item.label,
                    "is_active": menu_item.is_active,
                },
            )
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
