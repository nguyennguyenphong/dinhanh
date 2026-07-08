from __future__ import annotations

from branches.application.dtos.branch_dtos import BranchUpdateDto
from branches.domain.entities.branch_entity import BranchEntity
from branches.repositories.interfaces.branch_repository_interface import (
    IBranchRepository,
)


class UpdateBranchUseCase:

    def __init__(self, repo: IBranchRepository) -> None:
        self._repo = repo

    def execute(self, dto: BranchUpdateDto) -> BranchEntity:
        existing = self._repo.get_by_id(dto.id)
        if not existing:
            raise ValueError(f"Branch with ID {dto.id} not found.")

        existing.code = dto.code
        existing.name = dto.name
        existing.address = dto.address
        existing.phone = dto.phone
        existing.email = dto.email
        existing.manager_id = dto.manager_id
        existing.latitude = dto.latitude
        existing.longitude = dto.longitude
        existing.timezone = dto.timezone
        existing.is_active = dto.is_active
        existing.metadata = dto.metadata

        return self._repo.save(existing)
