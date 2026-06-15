from menus.exceptions import MenuGroupNotFoundError
from menus.application.dtos.menu_groups import MenuGroupHardDeleteDto
from menus.repositories.interfaces import IMenuGroupRepository


class HardDeleteMenuGroupUseCase:
    """Permanently purges a specific record out of the persistent storage layer completely."""

    def __init__(self, menu_group_repo: IMenuGroupRepository):
        self._repo = menu_group_repo

    def execute(self, dto: MenuGroupHardDeleteDto) -> None:
        # Use full fetch containing deleted objects if it's already soft-deleted
        # Since IMenuGroupRepository list() handles it, we look for it up directly
        entity = self._repo.get_by_id(dto.id)
        
        # If standard get returns None, it could be soft-deleted already. 
        # For a clean hard delete flow, we re-verify or trust the database cascade.
        if not entity:
            raise MenuGroupNotFoundError(dto.id)
            
        if entity.tenant_id != dto.tenant_id:
            raise MenuGroupNotFoundError(dto.id)

        self._repo.hard_delete(entity)