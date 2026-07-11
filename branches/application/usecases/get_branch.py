from __future__ import annotations

from branches.application.dtos import BranchDetailDto
from branches.repositories.interfaces.branch_repository_interface import (
    IBranchRepository,
)


class GetBranchUseCase:

    def __init__(self, repo: IBranchRepository) -> None:
        self._repo = repo

    def execute(self, branch_id: int) -> BranchDetailDto | None:
        entity = self._repo.get_by_id(branch_id)
        if not entity:
            return None

        return BranchDetailDto(
            id=entity.id,
            tenant_id=entity.tenant_id,
            code=entity.code,
            name=entity.name,
            address=entity.address,
            phone=entity.phone,
            email=entity.email,
            manager_id=entity.manager_id,
            latitude=entity.latitude,
            longitude=entity.longitude,
            timezone=entity.timezone,
            is_active=entity.is_active,
            metadata=entity.metadata,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
