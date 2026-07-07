from menus.application.dtos.menu_items import (
    MenuItemResponseDto,
    MenuItemUpdateDto,
)
from menus.application.usecases.menu_items.helper_mapping_menu_item_usecase import (
    _entity_to_response,
)
from menus.exceptions import (
    MenuItemAlreadyExistsError,
    MenuItemNotFoundError,
)
from menus.repositories.interfaces.menu_item_repository_interface import (
    IMenuItemRepository,
)


class UpdateMenuItemUseCase:
    """Orchestrates the business process for modifying an existing MenuItem."""

    def __init__(self, menu_item_repo: IMenuItemRepository):
        self._repo = menu_item_repo

    def execute(self, dto: MenuItemUpdateDto) -> MenuItemResponseDto:
        # Retrieve the existing domain entity or fail early
        entity = self._repo.get_by_id(dto.id)
        if not entity:
            raise MenuItemNotFoundError(dto.id)

        # Check uniqueness of code when code is modified
        normalized_code = dto.code.lower().strip()
        if self._repo.exists_with_code(
            tenant_id=entity.tenant_id, code=normalized_code, exclude_id=entity.id
        ):
            raise MenuItemAlreadyExistsError(
                tenant_id=entity.tenant_id, code=normalized_code
            )

        # Prevent circular reference
        if dto.parent_id is not None and dto.parent_id == entity.id:
            raise ValueError("Menu item cannot be its own parent.")

        # Enforce hierarchy depth and circular guards
        if dto.parent_id is not None:
            self._validate_hierarchy(dto.parent_id, entity.id)

        # Map DTO updates to the domain entity
        entity.code = normalized_code
        entity.label = dto.label.strip()
        entity.group_id = dto.group_id
        entity.parent_id = dto.parent_id
        entity.url_name = dto.url_name.strip() if dto.url_name else None
        entity.url_path = dto.url_path.strip() if dto.url_path else None
        entity.icon = dto.icon.strip() if dto.icon else None
        entity.badge = dto.badge.strip() if dto.badge else None
        entity.permission_code = (
            dto.permission_code.strip() if dto.permission_code else None
        )
        entity.sort_order = dto.sort_order
        entity.open_in_new_tab = dto.open_in_new_tab
        entity.is_active = dto.is_active
        entity.is_hidden = dto.is_hidden

        # Map to query arguments for update
        update_data = {
            "code": entity.code,
            "label": entity.label,
            "group_id": entity.group_id,
            "parent_id": entity.parent_id,
            "url_name": entity.url_name,
            "url_path": entity.url_path,
            "icon": entity.icon,
            "badge": entity.badge,
            "permission_code": entity.permission_code,
            "sort_order": entity.sort_order,
            "open_in_new_tab": entity.open_in_new_tab,
            "is_active": entity.is_active,
            "is_hidden": entity.is_hidden,
        }

        updated_entity = self._repo.update(entity, **update_data)
        return _entity_to_response(updated_entity)

    def _validate_hierarchy(self, parent_id: int, current_id: int) -> None:
        depth = 0
        visited = {current_id}
        curr_parent_id = parent_id

        while curr_parent_id:
            if curr_parent_id in visited:
                raise ValueError("Circular menu hierarchy detected.")
            visited.add(curr_parent_id)

            parent_node = self._repo.get_by_id(curr_parent_id)
            if not parent_node:
                break
            depth += 1
            curr_parent_id = parent_node.parent_id

        if depth >= 5:  # Maximum allowed depth is 5 levels
            raise ValueError("Maximum menu hierarchy depth (5) exceeded.")
