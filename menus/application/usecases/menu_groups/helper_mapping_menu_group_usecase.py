from menus.domain.entities import MenuGroupEntity
from menus.application.dtos.menu_groups import (
    MenuGroupDetailDto,
    MenuGroupResponseDto,
)


def _entity_to_response(entity: MenuGroupEntity) -> MenuGroupResponseDto:
    """Transforms a domain entity into a plain data response DTO."""
    return MenuGroupResponseDto.from_entity(entity)


def _entity_to_detail(entity: MenuGroupEntity) -> MenuGroupDetailDto:
    """Transforms a domain entity into a detail view DTO."""
    return MenuGroupDetailDto.from_entity(entity)