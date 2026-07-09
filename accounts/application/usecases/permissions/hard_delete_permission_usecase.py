from __future__ import annotations

import uuid

from accounts.repositories.interfaces.permission_repository_interface import (
    PermissionRepository,
)


class HardDeletePermissionUseCase:

    def __init__(self, repository: PermissionRepository):
        self._repo = repository

    def execute(self, permission_uuid: uuid.UUID) -> bool:
        entity = self._repo.find_by_uuid(permission_uuid)
        if not entity:
            raise ValueError("Không tìm thấy quyền hạn.")
        if entity.is_system:
            raise ValueError("Không thể xóa vĩnh viễn quyền hạn hệ thống (is_system).")
        return self._repo.hard_delete(permission_uuid)
