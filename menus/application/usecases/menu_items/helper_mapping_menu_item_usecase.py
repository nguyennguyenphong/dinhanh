from menus.application.dtos.menu_items import (
    MenuItemDetailDto,
    MenuItemResponseDto,
)
from menus.domain.entities.menu_item_entity import MenuItemEntity


def _entity_to_response(entity: MenuItemEntity) -> MenuItemResponseDto:
    """Transforms a MenuItem domain entity into a flat response DTO."""
    return MenuItemResponseDto.from_entity(entity)


def _entity_to_detail(entity: MenuItemEntity) -> MenuItemDetailDto:
    """Transforms a MenuItem domain entity into a detail DTO."""
    return MenuItemDetailDto.from_entity(entity)
