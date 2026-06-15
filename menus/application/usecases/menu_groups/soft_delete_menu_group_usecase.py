from menus.exceptions import MenuGroupNotFoundError
from menus.application.dtos.menu_groups import MenuGroupSoftDeleteDto
from menus.repositories.interfaces import IMenuGroupRepository


class SoftDeleteMenuGroupUseCase:
    """Safely flags a MenuGroup as invisible or moved to trash bin without destroying data."""

    def __init__(self, menu_group_repo: IMenuGroupRepository):
        self._repo = menu_group_repo

    def execute(self, dto: MenuGroupSoftDeleteDto) -> None:
        entity = self._repo.get_by_id(dto.id)
        if not entity or entity.tenant_id != dto.tenant_id:
            raise MenuGroupNotFoundError(dto.id)

        self._repo.soft_delete(entity)