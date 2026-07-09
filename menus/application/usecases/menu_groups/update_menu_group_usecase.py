from menus.application.dtos.menu_groups import (
    MenuGroupResponseDto,
    MenuGroupUpdateDto,
)
from menus.application.usecases.menu_groups.helper_mapping_menu_group_usecase import (
    _entity_to_response,
)
from menus.exceptions import (
    MenuGroupAlreadyExistsError,
    MenuGroupNotFoundError,
)
from menus.repositories.interfaces import IMenuGroupRepository


class UpdateMenuGroupUseCase:
    """Orchestrates the business process for modifying an existing MenuGroup."""

    def __init__(self, menu_group_repo: IMenuGroupRepository):
        self._repo = menu_group_repo

    def execute(self, dto: MenuGroupUpdateDto) -> MenuGroupResponseDto:
        # Retrieve the existing domain model or fail early
        entity = self._repo.get_by_id(dto.id)
        if not entity:
            raise MenuGroupNotFoundError(dto.id)

        # Business rule: If changing code, the new code must not collide with other existing groups
        normalized_code = dto.code.lower().strip()
        if self._repo.exists_by_code(
            tenant=entity.tenant_id, code=normalized_code, exclude_id=entity.id
        ):
            raise MenuGroupAlreadyExistsError(
                tenant_id=entity.tenant_id, code=normalized_code
            )

        if hasattr(self._repo, "exists_by_sort_order"):
            if self._repo.exists_by_sort_order(
                tenant=entity.tenant_id, sort_order=dto.sort_order, exclude_id=entity.id
            ):
                raise ValueError(
                    f"Thứ tự hiển thị {dto.sort_order} đã tồn tại."
                )

        # Delegate business logic updates to behaviors built directly inside the domain model
        entity.code = normalized_code
        entity.update_display(
            label=dto.label,
            icon=dto.icon,
            sort_order=dto.sort_order,
        )

        if dto.is_active:
            entity.activate()
        else:
            entity.deactivate()

        updated_entity = self._repo.update(entity)
        return _entity_to_response(updated_entity)
