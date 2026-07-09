from __future__ import annotations

import uuid

from accounts.repositories.interfaces.user_repository_interface import UserRepository


class SoftDeleteUserUseCase:

    def __init__(self, repository: UserRepository):
        self._repo = repository

    def execute(self, user_uuid: uuid.UUID) -> bool:
        return self._repo.delete(user_uuid)
