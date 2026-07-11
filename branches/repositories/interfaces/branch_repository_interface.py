from __future__ import annotations

from abc import ABC, abstractmethod

from branches.domain.entities.branch_entity import BranchEntity


class IBranchRepository(ABC):

    @abstractmethod
    def get_by_id(self, branch_id: int) -> BranchEntity | None:
        pass

    @abstractmethod
    def save(self, branch: BranchEntity) -> BranchEntity:
        pass

    @abstractmethod
    def delete(self, branch_id: int) -> None:
        pass

    @abstractmethod
    def hard_delete(self, branch_id: int) -> None:
        pass

    @abstractmethod
    def list(
        self,
        tenant_id: int,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[BranchEntity], int]:
        pass
