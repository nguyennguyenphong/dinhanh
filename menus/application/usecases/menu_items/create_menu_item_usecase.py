import uuid

from menus.application.dtos.menu_items import (
    MenuItemCreateDto,
    MenuItemResponseDto,
)
from menus.application.usecases.menu_items.helper_mapping_menu_item_usecase import (
    _entity_to_response,
)
from menus.domain.entities.menu_item_entity import MenuItemEntity
from menus.exceptions import MenuItemAlreadyExistsError
from menus.repositories.interfaces.menu_item_repository_interface import (
    IMenuItemRepository,
)


class CreateMenuItemUseCase:
    """Orchestrates the business process for creating a brand new MenuItem."""

    def __init__(self, menu_item_repo: IMenuItemRepository):
        self._repo = menu_item_repo

    def execute(self, dto: MenuItemCreateDto) -> MenuItemResponseDto:
        # Check uniqueness of code within the tenant context
        normalized_code = dto.code.lower().strip()
        if self._repo.exists_with_code(tenant_id=dto.tenant, code=normalized_code):
            raise MenuItemAlreadyExistsError(tenant_id=dto.tenant, code=normalized_code)

        # Enforce hierarchy depth and circular guards if parent is specified
        if dto.parent_id is not None:
            self._validate_hierarchy(dto.parent_id)

        # Build domain entity to automatically trigger self-invariants validation
        entity = MenuItemEntity(
            id=None,
            uuid=uuid.uuid4(),
            tenant_id=dto.tenant,
            code=normalized_code,
            label=dto.label.strip(),
            group_id=dto.group_id,
            parent_id=dto.parent_id,
            url_name=dto.url_name.strip() if dto.url_name else None,
            url_path=dto.url_path.strip() if dto.url_path else None,
            icon=dto.icon.strip() if dto.icon else None,
            badge=dto.badge.strip() if dto.badge else None,
            permission_code=(
                dto.permission_code.strip() if dto.permission_code else None
            ),
            sort_order=dto.sort_order,
            open_in_new_tab=dto.open_in_new_tab,
            is_active=dto.is_active,
            is_hidden=dto.is_hidden,
        )

        # Prepare kwargs for ORM creation matching expected repository signature
        creation_data = {
            "uuid": entity.uuid,
            "tenant_id": entity.tenant_id,
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

        saved_entity = self._repo.create(**creation_data)
        return _entity_to_response(saved_entity)

    def _validate_hierarchy(self, parent_id: int) -> None:
        depth = 0
        visited = set()
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
