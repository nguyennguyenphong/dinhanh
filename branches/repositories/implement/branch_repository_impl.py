from __future__ import annotations

from django.db.models import Q

from branches.domain.entities.branch_entity import BranchEntity
from branches.models import Branch
from branches.repositories.interfaces.branch_repository_interface import (
    IBranchRepository,
)


class BranchRepositoryImpl(IBranchRepository):

    def _to_entity(self, model: Branch) -> BranchEntity:
        return BranchEntity(
            id=model.id,
            tenant_id=model.tenant_id,
            code=model.code,
            name=model.name,
            address=model.address,
            phone=model.phone,
            email=model.email,
            manager_id=model.manager_id,
            latitude=model.latitude,
            longitude=model.longitude,
            timezone=model.timezone,
            is_active=model.is_active,
            metadata=model.metadata or {},
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def get_by_id(self, branch_id: int) -> BranchEntity | None:
        try:
            model = Branch.objects.get(id=branch_id)
            return self._to_entity(model)
        except Branch.DoesNotExist:
            return None

    def save(self, branch: BranchEntity) -> BranchEntity:
        data = {
            "tenant_id": branch.tenant_id,
            "code": branch.code,
            "name": branch.name,
            "address": branch.address,
            "phone": branch.phone,
            "email": branch.email,
            "manager_id": branch.manager_id,
            "latitude": branch.latitude,
            "longitude": branch.longitude,
            "timezone": branch.timezone,
            "is_active": branch.is_active,
            "metadata": branch.metadata,
        }

        if branch.id is not None:
            model, _ = Branch.objects.update_or_create(id=branch.id, defaults=data)
        else:
            model = Branch.objects.create(**data)

        return self._to_entity(model)

    def delete(self, branch_id: int) -> None:
        Branch.objects.filter(id=branch_id).delete()

    def list(
        self,
        tenant_id: int,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[BranchEntity], int]:
        queryset = Branch.objects.filter(tenant_id=tenant_id)

        if search:
            queryset = queryset.filter(
                Q(code__icontains=search) | Q(name__icontains=search)
            )

        total = queryset.count()
        models_list = queryset.order_by("code")[offset : offset + limit]
        entities = [self._to_entity(m) for m in models_list]
        return entities, total
