from typing import Optional

from django.db import transaction

from menus.domain.entities.menu_item_entity import MenuItemEntity
from menus.repositories.interfaces.menu_item_repository_interface import IMenuItemRepository


class MenuItemRepositoryImpl(IMenuItemRepository):
    """ORM-backed MenuItem repository."""

    def get_by_id(self, item_id: int) -> Optional[MenuItemEntity]:
        return (
            MenuItemEntity.objects.filter(pk=item_id)
            .select_related("tenant", "group", "parent")
            .first()
        )

    def get_by_uuid(self, uuid: str) -> Optional[MenuItemEntity]:
        return (
            MenuItemEntity.objects.filter(uuid=uuid)
            .select_related("tenant", "group", "parent")
            .first()
        )

    def get_by_code(self, tenant_id: int, code: str) -> Optional[MenuItemEntity]:
        return MenuItemEntity.objects.filter(tenant_id=tenant_id, code=code).first()

    def get_all_for_tenant(self, tenant_id: int):
        return (
            MenuItemEntity.objects.filter(tenant_id=tenant_id)
            .select_related("tenant", "group", "parent")
            .prefetch_related("children", "role_assignments__role")
            .order_by("sort_order", "code")
        )

    def get_for_group(self, group_id: int):
        return (
            MenuItemEntity.objects.filter(group_id=group_id)
            .select_related("group", "parent")
            .order_by("sort_order")
        )

    def get_root_items(self, tenant_id: int):
        return (
            MenuItemEntity.objects.filter(tenant_id=tenant_id, parent__isnull=True)
            .select_related("group")
            .prefetch_related("children")
            .order_by("sort_order")
        )

    def get_children(self, parent_id: int):
        return (
            MenuItemEntity.objects.filter(parent_id=parent_id)
            .order_by("sort_order")
        )

    @transaction.atomic
    def create(self, **kwargs) -> MenuItemEntity:
        return MenuItemEntity.objects.create(**kwargs)

    @transaction.atomic
    def update(self, item: MenuItemEntity, **kwargs) -> MenuItemEntity:
        for field, value in kwargs.items():
            setattr(item, field, value)
        item.save(update_fields=list(kwargs.keys()) + ["updated_at"])
        return item

    @transaction.atomic
    def delete(self, item: MenuItemEntity) -> None:
        item.delete()

    @transaction.atomic
    def bulk_reorder(self, tenant_id: int, order_data: list[dict]) -> None:
        """
        Efficiently update sort_order for multiple items.

        Args:
            tenant_id: Tenant PK (used for ownership check)
            order_data: [{'id': 1, 'sort_order': 0}, ...]
        """
        ids = [entry["id"] for entry in order_data]
        items = {
            item.pk: item
            for item in MenuItemEntity.objects.filter(pk__in=ids, tenant_id=tenant_id)
        }
        to_update = []
        for entry in order_data:
            item = items.get(entry["id"])
            if item:
                item.sort_order = entry["sort_order"]
                to_update.append(item)
        MenuItemEntity.objects.bulk_update(to_update, ["sort_order"])

    def exists_with_code(
        self,
        tenant_id: int,
        code: str,
        exclude_id: Optional[int] = None,
    ) -> bool:
        qs = MenuItemEntity.objects.filter(tenant_id=tenant_id, code=code)
        if exclude_id:
            qs = qs.exclude(pk=exclude_id)
        return qs.exists()