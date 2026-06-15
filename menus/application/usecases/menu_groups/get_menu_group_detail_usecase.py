from menus.application.dtos.menu_groups import MenuGroupDetailDto
from menus.application.usecases.menu_groups.helper_mapping_menu_group_usecase import (
    _entity_to_detail,
)
from menus.exceptions import MenuGroupNotFoundError
from menus.repositories.interfaces import IMenuGroupRepository


class GetMenuGroupDetailUseCase:
    """Fetches full details of a unique MenuGroup for presentation purposes."""

    def __init__(self, menu_group_repo: IMenuGroupRepository):
        self._repo = menu_group_repo

    def execute(self, menu_group_id: int) -> MenuGroupDetailDto:
        entity = self._repo.get_by_id(menu_group_id)
        if not entity:
            raise MenuGroupNotFoundError(menu_group_id)

        return _entity_to_detail(entity)
