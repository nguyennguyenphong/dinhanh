from __future__ import annotations

import uuid

from accounts.application.dtos.users.user_response_dto import UserResponseDto
from accounts.application.dtos.users.user_update_dto import UserUpdateDto
from accounts.repositories.interfaces.user_repository_interface import UserRepository


class UpdateUserUseCase:
    """Orchestrates user detail updating."""

    def __init__(self, repository: UserRepository):
        self._repo = repository

    def execute(self, user_uuid: uuid.UUID, dto: UserUpdateDto) -> UserResponseDto:
        entity = self._repo.find_by_uuid(user_uuid)
        if not entity:
            raise ValueError("Không tìm thấy người dùng.")

        entity.update_info(
            full_name=dto.full_name,
            phone=dto.phone,
            avatar=dto.avatar,
        )

        if dto.is_active:
            entity.activate()
        else:
            entity.deactivate()

        saved = self._repo.save(entity)
        return UserResponseDto.from_entity(saved)
