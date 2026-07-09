from __future__ import annotations

import uuid

from accounts.application.dtos.permissions.permission_create_dto import (
    PermissionCreateDto,
)
from accounts.application.dtos.permissions.permission_response_dto import (
    PermissionResponseDto,
)
from accounts.domain.entities.permission_entity import PermissionEntity
from accounts.repositories.interfaces.permission_repository_interface import (
    PermissionRepository,
)


class CreatePermissionUseCase:
    """Orchestrates permission creation and validation checks."""

    def __init__(self, repository: PermissionRepository):
        self._repo = repository

    def execute(self, dto: PermissionCreateDto) -> PermissionResponseDto:
        target_codename = dto.codename.strip().lower()

        if self._repo.exists_by_codename(
            tenant_id=dto.tenant_id, codename=target_codename
        ):
            raise ValueError("Mã codename cho quyền này đã tồn tại trong Tenant.")

        entity = PermissionEntity(
            id=None,
            uuid=uuid.uuid4(),
            tenant_id=dto.tenant_id,
            name=dto.name.strip(),
            codename=target_codename,
            module=dto.module.strip(),
            action=dto.action.strip(),
            parent_id=dto.parent_id,
            is_system=dto.is_system,
            is_active=dto.is_active,
        )

        saved = self._repo.save(entity)
        return PermissionResponseDto.from_entity(saved)
