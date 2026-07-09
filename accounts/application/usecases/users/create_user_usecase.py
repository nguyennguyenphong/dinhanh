from __future__ import annotations

import uuid
from django.contrib.auth.hashers import make_password

from accounts.application.dtos.users.user_create_dto import UserCreateDto
from accounts.application.dtos.users.user_response_dto import UserResponseDto
from accounts.domain.entities.user_entity import UserEntity
from accounts.repositories.interfaces.user_repository_interface import UserRepository


class CreateUserUseCase:
    """Orchestrates user creation and uniqueness validations."""

    def __init__(self, repository: UserRepository):
        self._repo = repository

    def execute(self, dto: UserCreateDto) -> UserResponseDto:
        normalized_username = dto.username.strip().lower()
        normalized_email = dto.email.strip().lower()

        if self._repo.exists_by_username(tenant_id=dto.tenant_id, username=normalized_username):
            raise ValueError("Tên đăng nhập đã tồn tại trong Tenant này.")

        if self._repo.exists_by_email(tenant_id=dto.tenant_id, email=normalized_email):
            raise ValueError("Email đã tồn tại trong Tenant này.")

        hashed = make_password(dto.password)

        entity = UserEntity(
            id=None,
            uuid=uuid.uuid4(),
            tenant_id=dto.tenant_id,
            username=normalized_username,
            email=normalized_email,
            full_name=dto.full_name.strip(),
            phone=dto.phone,
            avatar=dto.avatar,
            is_active=dto.is_active,
            hashed_password=hashed,
        )

        saved = self._repo.save(entity)
        return UserResponseDto.from_entity(saved)
