from __future__ import annotations

import uuid

from django.utils.text import slugify

from accounts.application.dtos.roles.role_create_dto import RoleCreateDto
from accounts.application.dtos.roles.role_response_dto import RoleResponseDto
from accounts.domain.entities.role_entity import RoleEntity
from accounts.repositories.interfaces.role_repository_interface import RoleRepository


class CreateRoleUseCase:
    """Orchestrates role creation and validations."""

    def __init__(self, repository: RoleRepository):
        self._repo = repository

    def execute(self, dto: RoleCreateDto) -> RoleResponseDto:
        target_slug = dto.slug.strip().lower() if dto.slug else slugify(dto.name)
        if not target_slug:
            raise ValueError("Role slug could not be generated.")

        if self._repo.exists_by_slug(tenant_id=dto.tenant_id, slug=target_slug):
            raise ValueError("Mã slug cho vai trò này đã tồn tại trong Tenant.")

        entity = RoleEntity(
            id=None,
            uuid=uuid.uuid4(),
            tenant_id=dto.tenant_id,
            name=dto.name.strip(),
            slug=target_slug,
            description=dto.description,
            is_system=dto.is_system,
            is_active=dto.is_active,
        )

        saved = self._repo.save(entity)
        return RoleResponseDto.from_entity(saved)
