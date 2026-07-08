from __future__ import annotations

from branches.application.dtos.branch_dtos import BranchCreateDto
from branches.domain.entities.branch_entity import BranchEntity
from branches.repositories.interfaces.branch_repository_interface import IBranchRepository


class CreateBranchUseCase:

    def __init__(self, repo: IBranchRepository) -> None:
        self._repo = repo

    def execute(self, dto: BranchCreateDto) -> BranchEntity:
        entity = BranchEntity(
            id=None,
            tenant_id=dto.tenant_id,
            code=dto.code,
            name=dto.name,
            address=dto.address,
            phone=dto.phone,
            email=dto.email,
            manager_id=dto.manager_id,
            latitude=dto.latitude,
            longitude=dto.longitude,
            timezone=dto.timezone,
            is_active=dto.is_active,
            metadata=dto.metadata,
        )
        return self._repo.save(entity)
