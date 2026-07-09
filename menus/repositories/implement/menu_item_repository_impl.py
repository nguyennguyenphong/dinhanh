from __future__ import annotations

import uuid
from typing import Any, Optional

from django.db import transaction
from django.db.models import Q
from safedelete.models import HARD_DELETE

from menus.domain.entities.menu_item_entity import MenuItemEntity
from menus.repositories.interfaces.menu_item_repository_interface import (
    IMenuItemRepository,
)


def _model_to_entity(obj: Any) -> MenuItemEntity:
    """Convert MenuItem ORM object to domain MenuItemEntity."""
    return MenuItemEntity(
        id=obj.pk,
        uuid=obj.uuid,
        tenant_id=obj.tenant_id,
        code=obj.code,
        label=obj.label,
        group_id=obj.group_id,
        parent_id=obj.parent_id,
        url_name=obj.url_name,
        url_path=obj.url_path,
        icon=obj.icon,
        badge=obj.badge_text,
        permission_code=obj.permission_code,
        sort_order=obj.sort_order,
        open_in_new_tab=obj.open_in_new_tab,
        is_active=obj.is_active,
        is_hidden=obj.is_hidden,
        created_at=obj.created_at,
        updated_at=obj.updated_at,
    )


class MenuItemRepositoryImpl(IMenuItemRepository):
    """ORM-backed MenuItem repository."""

    @property
    def _qs(self):
        from menus.models.menu_items import MenuItem

        return MenuItem.objects

    def get_by_id(self, item_id: int) -> Optional[MenuItemEntity]:
        obj = (
            self._qs.filter(pk=item_id)
            .select_related("tenant", "group", "parent")
            .first()
        )
        return _model_to_entity(obj) if obj else None

    def get_by_uuid(self, item_uuid: str | uuid.UUID) -> Optional[MenuItemEntity]:
        try:
            parsed = uuid.UUID(str(item_uuid))
        except ValueError:
            return None
        obj = (
            self._qs.filter(uuid=parsed)
            .select_related("tenant", "group", "parent")
            .first()
        )
        return _model_to_entity(obj) if obj else None

    def get_by_code(self, tenant_id: int, code: str) -> Optional[MenuItemEntity]:
        obj = self._qs.filter(tenant_id=tenant_id, code=code.lower()).first()
        return _model_to_entity(obj) if obj else None

    def get_all_for_tenant(self, tenant_id: int):
        qs = (
            self._qs.filter(tenant_id=tenant_id)
            .select_related("tenant", "group", "parent")
            .order_by("sort_order", "code")
        )
        return [_model_to_entity(obj) for obj in qs]

    def list(
        self,
        *,
        tenant_id: int,
        group_id: Optional[int] = None,
        parent_id: Optional[int] = None,
        filters: Optional[dict] = None,
        search: Optional[str] = None,
        ordering: Optional[list[str]] = None,
        limit: int = 20,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> tuple[list[MenuItemEntity], int]:
        from menus.models import MenuItem

        if include_deleted:
            qs = MenuItem.objects.all_with_deleted().filter(tenant_id=tenant_id)
        else:
            qs = self._qs.filter(tenant_id=tenant_id)

        if group_id is not None:
            qs = qs.filter(group_id=group_id)
        if parent_id is not None:
            qs = qs.filter(parent_id=parent_id)

        if filters:
            if filters.get("is_active") is not None:
                qs = qs.filter(is_active=filters["is_active"])

        if search:
            qs = qs.filter(Q(code__icontains=search) | Q(label__icontains=search))

        total = qs.count()

        allowed_orderings = {
            "created_at",
            "-created_at",
            "sort_order",
            "-sort_order",
            "code",
            "-code",
            "label",
            "-label",
        }
        if ordering:
            safe_ordering = [o for o in ordering if o in allowed_orderings]
            if safe_ordering:
                qs = qs.order_by(*safe_ordering)
        else:
            qs = qs.order_by("sort_order", "code")

        items = [_model_to_entity(obj) for obj in qs[offset : offset + limit]]
        return items, total

    def get_for_group(self, group_id: int):
        qs = (
            self._qs.filter(group_id=group_id)
            .select_related("group", "parent")
            .order_by("sort_order")
        )
        return [_model_to_entity(obj) for obj in qs]

    def get_root_items(self, tenant_id: int):
        qs = (
            self._qs.filter(tenant_id=tenant_id, parent__isnull=True)
            .select_related("group")
            .order_by("sort_order")
        )
        return [_model_to_entity(obj) for obj in qs]

    def get_children(self, parent_id: int):
        qs = self._qs.filter(parent_id=parent_id).order_by("sort_order")
        return [_model_to_entity(obj) for obj in qs]

    @transaction.atomic
    def create(self, **kwargs) -> MenuItemEntity:
        from menus.models.menu_items import MenuItem

        if "code" in kwargs:
            kwargs["code"] = kwargs["code"].lower()
        # Map entity attributes if passed from use-case
        if "badge" in kwargs:
            kwargs["badge_text"] = kwargs.pop("badge")
        obj = MenuItem.objects.create(**kwargs)
        return _model_to_entity(obj)

    @transaction.atomic
    def update(self, item: MenuItemEntity, **kwargs) -> MenuItemEntity:
        from menus.models.menu_items import MenuItem

        if "code" in kwargs:
            kwargs["code"] = kwargs["code"].lower()
        if "badge" in kwargs:
            kwargs["badge_text"] = kwargs.pop("badge")
        MenuItem.objects.filter(pk=item.id).update(**kwargs)
        updated_obj = MenuItem.objects.get(pk=item.id)
        return _model_to_entity(updated_obj)

    @transaction.atomic
    def delete(self, item: MenuItemEntity) -> None:
        from menus.models.menu_items import MenuItem

        if not item.id:
            return
        obj = MenuItem.objects.filter(pk=item.id).first()
        if obj:
            obj.delete()

    @transaction.atomic
    def hard_delete(self, item: MenuItemEntity) -> None:
        from menus.models.menu_items import MenuItem

        if not item.id:
            return
        obj = MenuItem.objects.all_with_deleted().filter(pk=item.id).first()
        if obj:
            obj.delete(force_policy=HARD_DELETE)

    @transaction.atomic
    def bulk_reorder(self, tenant_id: int, order_data: list[dict]) -> None:
        from menus.models.menu_items import MenuItem

        ids = [entry["id"] for entry in order_data]
        items = {
            item.pk: item
            for item in MenuItem.objects.filter(pk__in=ids, tenant_id=tenant_id)
        }
        to_update = []
        for entry in order_data:
            item = items.get(entry["id"])
            if item:
                item.sort_order = entry["sort_order"]
                to_update.append(item)
        MenuItem.objects.bulk_update(to_update, ["sort_order"])

    def exists_with_code(
        self,
        tenant_id: int,
        code: str,
        exclude_id: Optional[int] = None,
    ) -> bool:
        from menus.models.menu_items import MenuItem
        qs = MenuItem.objects.all_with_deleted().filter(tenant_id=tenant_id, code=code.lower())
        if exclude_id:
            qs = qs.exclude(pk=exclude_id)
        return qs.exists()

    def exists_by_sort_order(
        self,
        tenant_id: int,
        sort_order: int,
        exclude_id: Optional[int] = None,
    ) -> bool:
        from menus.models.menu_items import MenuItem
        qs = MenuItem.objects.all_with_deleted().filter(tenant_id=tenant_id, sort_order=sort_order)
        if exclude_id:
            qs = qs.exclude(pk=exclude_id)
        return qs.exists()
