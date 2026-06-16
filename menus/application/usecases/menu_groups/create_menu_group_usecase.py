import uuid

from menus.application.dtos.menu_groups import (
    MenuGroupCreateDto,
    MenuGroupResponseDto,
)
from menus.application.usecases.menu_groups.helper_mapping_menu_group_usecase import (
    _entity_to_response,
)
from menus.domain.entities import MenuGroupEntity
from menus.exceptions import MenuGroupAlreadyExistsError
from menus.repositories.interfaces import IMenuGroupRepository


class CreateMenuGroupUseCase:
    """Orchestrates the business process for creating a brand new MenuGroup."""

    def __init__(self, menu_group_repo: IMenuGroupRepository):
        self._repo = menu_group_repo

    def execute(self, dto: MenuGroupCreateDto) -> MenuGroupResponseDto:
        # Business rule: Code must be unique within the same tenant context
        normalized_code = dto.code.lower().strip()
        if self._repo.exists_by_code(tenant=dto.tenant, code=normalized_code):
            raise MenuGroupAlreadyExistsError(
                tenant_id=dto.tenant, code=normalized_code
            )

        if hasattr(self._repo, "exists_by_sort_order"):
            if self._repo.exists_by_sort_order(
                tenant=dto.tenant, sort_order=dto.sort_order
            ):
                raise ValueError(
                    f"Sort order {dto.sort_order} already exists for this tenant."
                )

        # Initialize the domain entity to automatically trigger self-invariants checking
        entity = MenuGroupEntity(
            id=None,
            uuid=uuid.uuid4(),
            tenant_id=dto.tenant,
            code=normalized_code,
            label=dto.label.strip(),
            icon=dto.icon.strip() if dto.icon else None,
            sort_order=dto.sort_order,
            is_active=dto.is_active,
        )

        saved_entity = self._repo.create(entity)
        return _entity_to_response(saved_entity)
