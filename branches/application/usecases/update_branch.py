from branches.application.dtos import BranchUpdateDto
from branches.domain.entities.branch_entity import BranchEntity
from branches.repositories.interfaces.branch_audit_log_repository_interface import (
    IBranchAuditLogRepository,
)
from branches.repositories.interfaces.branch_repository_interface import (
    IBranchRepository,
)


def _entity_to_dict(entity: BranchEntity) -> dict:
    return {
        "code": entity.code,
        "name": entity.name,
        "address": entity.address,
        "phone": entity.phone,
        "email": entity.email,
        "manager_id": entity.manager_id,
        "latitude": str(entity.latitude) if entity.latitude is not None else None,
        "longitude": str(entity.longitude) if entity.longitude is not None else None,
        "timezone": entity.timezone,
        "is_active": entity.is_active,
        "metadata": entity.metadata,
    }


class UpdateBranchUseCase:

    def __init__(
        self, repo: IBranchRepository, audit_repo: IBranchAuditLogRepository
    ) -> None:
        self._repo = repo
        self._audit_repo = audit_repo

    def execute(
        self,
        dto: BranchUpdateDto,
        *,
        actor_id: int | None = None,
        actor_username: str | None = None,
    ) -> BranchEntity:
        existing = self._repo.get_by_id(dto.id)
        if not existing:
            raise ValueError(f"Branch with ID {dto.id} not found.")

        old_values = _entity_to_dict(existing)

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

        saved = self._repo.save(existing)
        new_values = _entity_to_dict(saved)

        self._audit_repo.create_log(
            tenant_id=saved.tenant_id,
            branch_id=saved.id,
            action="UPDATE",
            actor_id=actor_id,
            actor_username=actor_username,
            old_values=old_values,
            new_values=new_values,
        )

        return saved
