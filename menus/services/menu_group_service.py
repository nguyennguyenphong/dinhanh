import uuid

from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404

from menus.application.dtos.menu_groups import (
    MenuGroupCreateDto,
    MenuGroupResponseDto,
    MenuGroupUpdateDto,
)
from menus.exceptions import MenuGroupDomainError
from menus.models import MenuGroup
from menus.providers import MenuGroupProvider
from menus.serializers.menu_groups import (
    MenuGroupCreateSerializer,
    MenuGroupUpdateSerializer,
)


class MenuGroupService:

    @staticmethod
    def get_menu_group_detail(request, pk: uuid.UUID) -> bool:
        """
        Detail menu group by uuid
        """
        menu_group = get_object_or_404(MenuGroup.all_objects, uuid=pk)
        if menu_group:
            MenuGroupProvider.get_menu_group_detail().execute(menu_group.id)

            return True
        else:
            messages.error(request, "Không tìm thấy nhóm menu")

    @staticmethod
    def create_menu_group(request, form) -> bool:
        """
        Returns True if successful, False if unsuccessful.
        Errors are pushed directly to the form to be displayed on the UI.
        """
        data = form.cleaned_data.copy()

        tenant_obj = data.get("tenant")
        if tenant_obj and hasattr(tenant_obj, "pk"):
            data["tenant"] = tenant_obj.pk

        repo_instance = MenuGroupProvider._menu_group_repo()

        # Validate with Serializer
        serializer = MenuGroupCreateSerializer(
            data=data, context={"menu_group_repo": repo_instance}
        )

        if not serializer.is_valid():
            for field, errors in serializer.errors.items():
                clean_errors = [str(err) for err in errors]

                target_field = field if field in form.fields else None
                form.add_error(target_field, clean_errors)

                messages.error(request, f"{field}: {clean_errors[0]}")
            return False

        validated_data = serializer.validated_data

        # Execute UseCase
        try:
            dto = MenuGroupCreateDto(**validated_data)
            MenuGroupProvider.create_menu_group().execute(dto)

            # Log MenuGroup creation
            from menus.models.menu_audit_log import MenuAuditLog
            MenuAuditLog.objects.create(
                tenant_id=validated_data["tenant"],
                action="CREATE",
                actor_id=request.user.id if request.user.is_authenticated else None,
                new_values={
                    "code": validated_data.get("code"),
                    "label": validated_data.get("label"),
                    "icon": validated_data.get("icon"),
                    "sort_order": validated_data.get("sort_order"),
                    "is_active": validated_data.get("is_active"),
                }
            )
            return True
        except Exception as exc:
            form.add_error(None, str(exc))
            messages.error(request, str(exc).replace("\n", " ").strip())
            return False

    @staticmethod
    def update_menu_group(request, pk: uuid.UUID, form) -> bool:
        menu_group_model = get_object_or_404(MenuGroup, uuid=pk)

        data = form.cleaned_data.copy()
        data["id"] = menu_group_model.id
        data["uuid"] = menu_group_model.uuid

        # 2. Validate serializer
        serializer = MenuGroupUpdateSerializer(
            data=data, context={"menu_group_model_id": menu_group_model.id}
        )
        if not serializer.is_valid():
            for field, errors in serializer.errors.items():
                target_field = field if field in form.fields else None
                form.add_error(target_field, errors)
            return False

        check_data = {
            "code": serializer.validated_data.get("code"),
            "label": serializer.validated_data.get("label"),
            "icon": serializer.validated_data.get("icon"),
            "sort_order": serializer.validated_data.get("sort_order"),
            "is_active": serializer.validated_data.get("is_active"),
        }
        model_data = {
            "code": menu_group_model.code,
            "label": menu_group_model.label,
            "icon": menu_group_model.icon,
            "sort_order": menu_group_model.sort_order,
            "is_active": menu_group_model.is_active,
        }
        if check_data == model_data:
            messages.info(request, "Dữ liệu không thay đổi.")
            return False

        try:
            dto = MenuGroupUpdateDto(**serializer.validated_data)

            # Capture old state before update
            old_values = {
                "code": menu_group_model.code,
                "label": menu_group_model.label,
                "icon": menu_group_model.icon,
                "sort_order": menu_group_model.sort_order,
                "is_active": menu_group_model.is_active,
            }

            MenuGroupProvider.update_menu_group().execute(dto)

            # Log MenuGroup update
            from menus.models.menu_audit_log import MenuAuditLog
            MenuAuditLog.objects.create(
                tenant_id=menu_group_model.tenant_id,
                action="UPDATE",
                actor_id=request.user.id if request.user.is_authenticated else None,
                old_values=old_values,
                new_values={
                    "code": serializer.validated_data.get("code"),
                    "label": serializer.validated_data.get("label"),
                    "icon": serializer.validated_data.get("icon"),
                    "sort_order": serializer.validated_data.get("sort_order"),
                    "is_active": serializer.validated_data.get("is_active"),
                }
            )

            return True
        except (MenuGroupDomainError, ValueError) as exc:
            form.add_error(None, str(exc))
            messages.error(request, str(exc))
            return False

    @staticmethod
    def soft_delete_menu_group(request, pk: uuid.UUID, form) -> bool:
        """
        Handle (Soft Delete) menu group.
        """
        menu_group = get_object_or_404(MenuGroup.all_objects, uuid=pk)
        try:
            from menus.application.dtos.menu_groups import MenuGroupSoftDeleteDto
            dto = MenuGroupSoftDeleteDto(
                id=menu_group.id,
                tenant_id=menu_group.tenant_id,
            )

            MenuGroupProvider.soft_delete_menu_group().execute(dto)

            # Log MenuGroup soft delete
            from menus.models.menu_audit_log import MenuAuditLog
            MenuAuditLog.objects.create(
                tenant_id=menu_group.tenant_id,
                action="DELETE",
                actor_id=request.user.id if request.user.is_authenticated else None,
                old_values={
                    "code": menu_group.code,
                    "label": menu_group.label,
                    "is_active": menu_group.is_active,
                }
            )
            return True

        except MenuGroupDomainError as exc:
            form.add_error(None, str(exc))
            messages.error(request, str(exc))
            return False

        except Exception:
            form.add_error(None, "Đã xảy ra lỗi không xác định khi xóa nhóm menu.")
            messages.error(request, "Có lỗi trong quá trình thực hiện.")
            return False

    @staticmethod
    def hard_delete_menu_group(request, pk: uuid.UUID, form) -> bool:
        """
        Handle (Hard Delete) menu group.
        """
        menu_group = get_object_or_404(MenuGroup.all_objects, uuid=pk)
        try:
            from menus.application.dtos.menu_groups import MenuGroupHardDeleteDto
            dto = MenuGroupHardDeleteDto(
                id=menu_group.id,
                tenant_id=menu_group.tenant_id,
            )
            MenuGroupProvider.hard_delete_menu_group().execute(dto)

            # Log MenuGroup hard delete
            from menus.models.menu_audit_log import MenuAuditLog
            MenuAuditLog.objects.create(
                tenant_id=menu_group.tenant_id,
                action="DELETE",
                actor_id=request.user.id if request.user.is_authenticated else None,
                old_values={
                    "code": menu_group.code,
                    "label": menu_group.label,
                    "is_active": menu_group.is_active,
                }
            )
            return True
        except Exception as exc:
            form.add_error(None, str(exc))
            messages.error(request, str(exc))
            return False

        except Exception as exc:
            form.add_error(None, "Đã xảy ra lỗi không xác định khi xóa nhóm menu.")
            messages.error(request, f"Lỗi xóa vĩnh viễn: {str(exc)}")
            return False

    @staticmethod
    def get_by_uuid(pk: uuid.UUID) -> MenuGroupResponseDto:
        menu_groups = get_object_or_404(MenuGroup.all_objects, uuid=pk)
        menu_group_id = menu_groups.id
        try:
            return MenuGroupProvider.get_menu_group_detail().execute(menu_group_id)
        except Exception:
            raise Http404("Nhóm menu không tồn tại")
