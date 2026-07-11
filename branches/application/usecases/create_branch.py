from branches.application.dtos import BranchCreateDto
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


class CreateBranchUseCase:

    def __init__(
        self, repo: IBranchRepository, audit_repo: IBranchAuditLogRepository
    ) -> None:
        self._repo = repo
        self._audit_repo = audit_repo

    def execute(
        self,
        dto: BranchCreateDto,
        *,
        actor_id: int | None = None,
        actor_username: str | None = None,
    ) -> BranchEntity:
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
        saved = self._repo.save(entity)

        self._audit_repo.create_log(
            tenant_id=saved.tenant_id,
            branch_id=saved.id,
            action="CREATE",
            actor_id=actor_id,
            actor_username=actor_username,
            new_values=_entity_to_dict(saved),
        )

        return saved
