from __future__ import annotations

import uuid

from accounts.repositories.interfaces.user_repository_interface import UserRepository


class HardDeleteUserUseCase:

    def __init__(self, repository: UserRepository):
        self._repo = repository

    def execute(self, user_uuid: uuid.UUID) -> bool:
        return self._repo.hard_delete(user_uuid)
