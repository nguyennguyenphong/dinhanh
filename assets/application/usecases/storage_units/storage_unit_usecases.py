from __future__ import annotations

from assets.application.dtos.storage_units.storage_unit_dtos import (
    StorageUnitCreateDto,
    StorageUnitResponseDto,
    StorageUnitUpdateDto,
)
from assets.domain.entities.storage_unit_entity import StorageUnitEntity
from assets.repositories.interfaces.storage_unit_repository_interface import (
    IStorageUnitRepository,
)


def entity_to_response(entity: StorageUnitEntity) -> StorageUnitResponseDto:
    return StorageUnitResponseDto(
        id=entity.id,
        tenant_id=entity.tenant_id,
        branch_id=entity.branch_id,
        code=entity.code,
        name=entity.name,
        description=entity.description,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


class CreateStorageUnitUseCase:

    def __init__(self, repo: IStorageUnitRepository):
        self._repo = repo

    def execute(self, dto: StorageUnitCreateDto) -> StorageUnitResponseDto:
        normalized_code = dto.code.strip().upper()
        if self._repo.exists_by_code(tenant_id=dto.tenant_id, code=normalized_code):
            raise ValueError(f"Storage unit with code '{normalized_code}' already exists.")

        entity = StorageUnitEntity(
            id=None,
            tenant_id=dto.tenant_id,
            branch_id=dto.branch_id,
            code=normalized_code,
            name=dto.name.strip(),
            description=dto.description,
        )
        saved = self._repo.create(entity)
        return entity_to_response(saved)


class UpdateStorageUnitUseCase:

    def __init__(self, repo: IStorageUnitRepository):
        self._repo = repo

    def execute(self, dto: StorageUnitUpdateDto) -> StorageUnitResponseDto:
        entity = self._repo.get_by_id(dto.id)
        if not entity:
            raise ValueError(f"StorageUnit with id {dto.id} not found.")

        normalized_code = dto.code.strip().upper()
        if self._repo.exists_by_code(tenant_id=entity.tenant_id, code=normalized_code, exclude_id=dto.id):
            raise ValueError(f"Storage unit with code '{normalized_code}' already exists.")

        entity.code = normalized_code
        entity.name = dto.name.strip()
        entity.description = dto.description
        entity.branch_id = dto.branch_id

        saved = self._repo.update(entity)
        return entity_to_response(saved)


class DeleteStorageUnitUseCase:

    def __init__(self, repo: IStorageUnitRepository):
        self._repo = repo

    def execute(self, storage_unit_id: int) -> None:
        entity = self._repo.get_by_id(storage_unit_id)
        if not entity:
            raise ValueError(f"StorageUnit with id {storage_unit_id} not found.")
        self._repo.delete(storage_unit_id)


class GetStorageUnitDetailUseCase:

    def __init__(self, repo: IStorageUnitRepository):
        self._repo = repo

    def execute(self, storage_unit_id: int) -> StorageUnitResponseDto | None:
        entity = self._repo.get_by_id(storage_unit_id)
        return entity_to_response(entity) if entity else None


class ListStorageUnitsUseCase:

    def __init__(self, repo: IStorageUnitRepository):
        self._repo = repo

    def execute(
        self,
        tenant_id: int,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[StorageUnitResponseDto], int]:
        entities, total = self._repo.list(
            tenant_id=tenant_id,
            search=search,
            limit=limit,
            offset=offset,
        )
        return [entity_to_response(e) for e in entities], total
