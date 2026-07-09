from __future__ import annotations

import uuid

from accounts.application.dtos.permissions.permission_update_dto import PermissionUpdateDto
from accounts.application.dtos.permissions.permission_response_dto import PermissionResponseDto
from accounts.repositories.interfaces.permission_repository_interface import PermissionRepository


class UpdatePermissionUseCase:
    """Orchestrates permission updates and validation checks."""

    def __init__(self, repository: PermissionRepository):
        self._repo = repository

    def execute(self, permission_uuid: uuid.UUID, dto: PermissionUpdateDto) -> PermissionResponseDto:
        entity = self._repo.find_by_uuid(permission_uuid)
        if not entity:
            raise ValueError("Không tìm thấy quyền hạn.")

        target_codename = dto.codename.strip().lower()
        if self._repo.exists_by_codename(tenant_id=entity.tenant_id, codename=target_codename, exclude_id=entity.id):
            raise ValueError("Mã codename cho quyền này đã tồn tại trong Tenant.")

        # Circular hierarchy check
        if dto.parent_id and dto.parent_id == entity.id:
            raise ValueError("Permission cannot be its own parent.")

        entity.update_info(
            name=dto.name,
            codename=target_codename,
            module=dto.module,
            action=dto.action,
            parent_id=dto.parent_id,
            is_active=dto.is_active,
        )

        saved = self._repo.save(entity)
        return PermissionResponseDto.from_entity(saved)
