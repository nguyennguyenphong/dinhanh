from __future__ import annotations

import uuid

from accounts.repositories.interfaces.role_repository_interface import RoleRepository


class SoftDeleteRoleUseCase:

    def __init__(self, repository: RoleRepository):
        self._repo = repository

    def execute(self, role_uuid: uuid.UUID) -> bool:
        entity = self._repo.find_by_uuid(role_uuid)
        if not entity:
            raise ValueError("Không tìm thấy vai trò.")
        if entity.is_system:
            raise ValueError("Không thể xóa vai trò hệ thống (is_system).")
        return self._repo.delete(role_uuid)
