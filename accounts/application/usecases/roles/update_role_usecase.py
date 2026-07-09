from __future__ import annotations

import uuid

from accounts.application.dtos.roles.role_update_dto import RoleUpdateDto
from accounts.application.dtos.roles.role_response_dto import RoleResponseDto
from accounts.repositories.interfaces.role_repository_interface import RoleRepository


class UpdateRoleUseCase:
    """Orchestrates role updates and validation checks."""

    def __init__(self, repository: RoleRepository):
        self._repo = repository

    def execute(self, role_uuid: uuid.UUID, dto: RoleUpdateDto) -> RoleResponseDto:
        entity = self._repo.find_by_uuid(role_uuid)
        if not entity:
            raise ValueError("Không tìm thấy vai trò.")

        target_slug = dto.slug.strip().lower()
        if self._repo.exists_by_slug(tenant_id=entity.tenant_id, slug=target_slug, exclude_id=entity.id):
            raise ValueError("Mã slug cho vai trò này đã tồn tại trong Tenant.")

        entity.update_info(
            name=dto.name,
            slug=target_slug,
            description=dto.description,
            is_active=dto.is_active,
        )

        saved = self._repo.save(entity)
        return RoleResponseDto.from_entity(saved)
