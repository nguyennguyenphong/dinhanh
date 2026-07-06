from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from menus.application.dtos.menu_groups.menu_group_response_dto import (
    MenuGroupResponseDto,
)


@dataclass(frozen=True)
class MenuGroupListDto:
    """
    The list data has been hashed (pagination), the optimal structure for the Template
    to render the `{% for item in menu_groups %}` loops and the pagination navigation bar.
    """

    items: list[MenuGroupResponseDto]
    total_count: int
    limit: int
    offset: int

    @property
    def has_next(self) -> bool:
        return self.offset + self.limit < self.total_count

    @property
    def has_previous(self) -> bool:
        return self.offset > 0

    @classmethod
    def from_entities(
        cls, entities: list[Any], total_count: int, limit: int, offset: int
    ) -> MenuGroupListDto:
        """Helper for quickly packaging the results returned from `Repository.list()`"""
        return cls(
            items=[MenuGroupResponseDto.from_entity(e) for e in entities],
            total_count=total_count,
            limit=limit,
            offset=offset,
        )
