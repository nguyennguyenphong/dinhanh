from __future__ import annotations

from branches.application.dtos.branch_dtos import BranchDetailDto
from branches.repositories.interfaces.branch_repository_interface import (
    IBranchRepository,
)


class ListBranchesUseCase:

    def __init__(self, repo: IBranchRepository) -> None:
        self._repo = repo

    def execute(
        self,
        tenant_id: int,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[BranchDetailDto], int]:
        entities, total = self._repo.list(
            tenant_id=tenant_id, search=search, limit=limit, offset=offset
        )

        dtos = [
            BranchDetailDto(
                id=e.id,
                tenant_id=e.tenant_id,
                code=e.code,
                name=e.name,
                address=e.address,
                phone=e.phone,
                email=e.email,
                manager_id=e.manager_id,
                latitude=e.latitude,
                longitude=e.longitude,
                timezone=e.timezone,
                is_active=e.is_active,
                metadata=e.metadata,
                created_at=e.created_at,
                updated_at=e.updated_at,
            )
            for e in entities
        ]

        return dtos, total
