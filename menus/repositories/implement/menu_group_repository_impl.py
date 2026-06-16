"""
Django ORM concrete implementation of IMenuGroupRepository.
All DB queries live here; the rest of the app never touches ORM directly.
"""

from __future__ import annotations

import uuid
from typing import Any

from django.db.models import Q
from safedelete.models import HARD_DELETE

from menus.domain.entities import MenuGroupEntity
from menus.repositories.interfaces import IMenuGroupRepository


def _model_to_entity(obj: Any) -> MenuGroupEntity:
    """Convert a MenuGroup ORM instance to a domain MenuGroupEntity."""
    return MenuGroupEntity(
        id=obj.pk,
        uuid=obj.uuid,
        tenant_id=obj.tenant_id,
        code=obj.code,
        label=obj.label,
        icon=obj.icon,
        sort_order=obj.sort_order,
        is_active=obj.is_active,
        created_at=obj.created_at,
        updated_at=obj.updated_at,
    )


class MenuGroupRepositoryImpl(IMenuGroupRepository):

    @property
    def _qs(self):
        """Lazy import to avoid circular imports at module load time."""
        from menus.models import MenuGroup

        return MenuGroup.objects

    # ------------------------------------------------------------------ #
    # Read operations                                                    #
    # ------------------------------------------------------------------ #

    def get_by_id(self, menu_group_id: int) -> MenuGroupEntity | None:
        obj = self._qs.filter(pk=menu_group_id).first()
        return _model_to_entity(obj) if obj else None

    def get_by_uuid(self, group_uuid: uuid.UUID) -> MenuGroupEntity | None:
        try:
            parsed = uuid.UUID(str(group_uuid))
        except ValueError:
            return None
        obj = self._qs.filter(uuid=parsed).first()
        return _model_to_entity(obj) if obj else None

    def get_by_code(self, tenant: int, code: str) -> MenuGroupEntity | None:
        obj = self._qs.filter(tenant_id=tenant, code=code.lower()).first()
        return _model_to_entity(obj) if obj else None

    def list(
        self,
        *,
        tenant_id: int,
        filters: dict[str, Any] | None = None,
        search: str | None = None,
        ordering: list[str] | None = None,
        limit: int = 20,
        offset: int = 0,
        include_deleted: bool = False,
    ) -> tuple[list[MenuGroupEntity], int]:
        from menus.models import MenuGroup

        # Toggle soft-deleted filter based on requirement
        if include_deleted:
            qs = MenuGroup.objects.all_with_deleted().filter(tenant_id=tenant_id)
        else:
            qs = self._qs.filter(tenant_id=tenant_id)

        # Apply structured filters
        if filters:
            if filters.get("is_active") is not None:
                qs = qs.filter(is_active=filters["is_active"])

        # Full-text search across code, label
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

    def exists_by_code(
        self, tenant: int, code: str, exclude_id: int | None = None
    ) -> bool:
        qs = self._qs.filter(tenant_id=tenant, code=code.lower())
        if exclude_id:
            qs = qs.exclude(pk=exclude_id)
        return qs.exists()
    
    def exists_by_sort_order(self, tenant: int, sort_order: int, exclude_id: int | None = None) -> bool:
        qs = self._qs.filter(tenant_id=tenant, sort_order=sort_order)
        if exclude_id:
            qs = qs.exclude(pk=exclude_id)
        return qs.exists()

    # ------------------------------------------------------------------ #
    # Write operations                                                   #
    # ------------------------------------------------------------------ #

    def create(self, entity: MenuGroupEntity) -> MenuGroupEntity:
        from menus.models import MenuGroup

        obj = MenuGroup.objects.create(
            uuid=entity.uuid,
            tenant_id=entity.tenant_id,
            code=entity.code.lower(),
            label=entity.label,
            icon=entity.icon,
            sort_order=entity.sort_order,
            is_active=entity.is_active,
        )
        return _model_to_entity(obj)

    def update(self, entity: MenuGroupEntity) -> MenuGroupEntity:
        from menus.models import MenuGroup

        MenuGroup.objects.filter(pk=entity.id).update(
            code=entity.code.lower(),
            label=entity.label,
            icon=entity.icon,
            sort_order=entity.sort_order,
            is_active=entity.is_active,
        )
        return self.get_by_id(entity.id)  # type: ignore[return-value]

    def soft_delete(self, entity: MenuGroupEntity) -> None:
        """Executes a standard soft delete using django-safedelete policy."""
        from menus.models import MenuGroup

        if not entity.id:
            return

        obj = MenuGroup.objects.filter(pk=entity.id).first()
        if obj:
            obj.delete()

    def hard_delete(self, entity: MenuGroupEntity) -> None:
        """CRITICAL: Force purges the record entirely from the DB."""
        from menus.models import MenuGroup

        if not entity.id:
            return

        obj = MenuGroup.objects.all_with_deleted().filter(pk=entity.id).first()
        if obj:
            obj.delete(force_policy=HARD_DELETE)
