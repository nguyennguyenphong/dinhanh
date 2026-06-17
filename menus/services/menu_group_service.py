import uuid

from django.contrib import messages
from django.shortcuts import get_object_or_404

from django.http import Http404

from menus.application.dtos.menu_groups import (
    MenuGroupCreateDto,
    MenuGroupUpdateDto,
    MenuGroupResponseDto
)
from menus.exceptions import MenuGroupDomainError
from menus.models import MenuGroup
from menus.providers import MenuGroupProvider
from menus.serializers.menu_groups import (
    MenuGroupCreateSerializer,
    MenuGroupUpdateSerializer,
)
from menus.utils.request_helpers import get_client_ip
from menus.views.helpers.view_helpers import RequestContext


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
            return True
        except Exception as exc:
            form.add_error(None, str(exc))
            messages.error(request, str(exc).replace("\n", " ").strip())
            return False

    @staticmethod
    def update_menu_group(request, pk: uuid.UUID, form) -> bool:
        menu_group_model = get_object_or_404(MenuGroup, uuid=pk)

        data = form.cleaned_data.copy()

        # 2. Validate serializer
        serializer = MenuGroupUpdateSerializer(
            data=data, context={"menu_group_model_id": menu_group_model.id}
        )
        if not serializer.is_valid():
            for field, errors in serializer.errors.items():
                form.add_error(field, errors)
            return False

        try:
            ctx = RequestContext.from_request(request)
            dto = MenuGroupUpdateDto(
                menu_group_model_id=menu_group_model.id, **serializer.validated_data
            )

            MenuGroupProvider.update_menu_group().execute(
                dto,
                actor_id=ctx.actor_id,
                actor_username=ctx.actor_username,
                ip_address=get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )

            return True
        except MenuGroupDomainError as exc:
            form.add_error(None, str(exc))
            return False

    @staticmethod
    def soft_delete_menu_group(request, pk: uuid.UUID, form) -> bool:
        """
        Handle (Soft Delete) menu group.
        """
        menu_group = get_object_or_404(MenuGroup.all_objects, uuid=pk)
        try:
            ctx = RequestContext.from_request(request)

            MenuGroupProvider.soft_delete_menu_group().execute(
                menu_group.id,
                actor_id=ctx.actor_id,
                actor_username=ctx.actor_username,
                ip_address=get_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )

            return True

        except MenuGroupDomainError as exc:
            form.add_error(None, str(exc))
            messages.error(request, str(exc))
            return False

        except Exception as exc:
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
            ctx = RequestContext.from_request(request)
            MenuGroupProvider.hard_delete_menu_group().execute(
                menu_group.id,
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