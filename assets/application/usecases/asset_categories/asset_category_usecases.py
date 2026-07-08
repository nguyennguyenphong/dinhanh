from __future__ import annotations

from assets.application.dtos.asset_categories.asset_category_dtos import (
    AssetCategoryCreateDto,
    AssetCategoryResponseDto,
    AssetCategoryUpdateDto,
)
from assets.domain.entities.asset_category_entity import AssetCategoryEntity
from assets.repositories.interfaces.asset_category_repository_interface import (
    IAssetCategoryRepository,
)


def entity_to_response(entity: AssetCategoryEntity) -> AssetCategoryResponseDto:
    return AssetCategoryResponseDto(
        id=entity.id,
        tenant_id=entity.tenant_id,
        name=entity.name,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


class CreateAssetCategoryUseCase:

    def __init__(self, repo: IAssetCategoryRepository):
        self._repo = repo

    def execute(self, dto: AssetCategoryCreateDto) -> AssetCategoryResponseDto:
        normalized_name = dto.name.strip()
        if self._repo.exists_by_name(tenant_id=dto.tenant_id, name=normalized_name):
            raise ValueError(f"Category with name '{normalized_name}' already exists.")

        entity = AssetCategoryEntity(
            id=None,
            tenant_id=dto.tenant_id,
            name=normalized_name,
        )
        saved = self._repo.create(entity)
        return entity_to_response(saved)


class UpdateAssetCategoryUseCase:

    def __init__(self, repo: IAssetCategoryRepository):
        self._repo = repo

    def execute(self, dto: AssetCategoryUpdateDto) -> AssetCategoryResponseDto:
        entity = self._repo.get_by_id(dto.id)
        if not entity:
            raise ValueError(f"AssetCategory with id {dto.id} not found.")

        normalized_name = dto.name.strip()
        if self._repo.exists_by_name(
            tenant_id=entity.tenant_id, name=normalized_name, exclude_id=dto.id
        ):
            raise ValueError(f"Category with name '{normalized_name}' already exists.")

        entity.name = normalized_name
        saved = self._repo.update(entity)
        return entity_to_response(saved)


class DeleteAssetCategoryUseCase:

    def __init__(self, repo: IAssetCategoryRepository):
        self._repo = repo

    def execute(self, category_id: int) -> None:
        entity = self._repo.get_by_id(category_id)
        if not entity:
            raise ValueError(f"AssetCategory with id {category_id} not found.")
        self._repo.delete(category_id)


class GetAssetCategoryDetailUseCase:

    def __init__(self, repo: IAssetCategoryRepository):
        self._repo = repo

    def execute(self, category_id: int) -> AssetCategoryResponseDto | None:
        entity = self._repo.get_by_id(category_id)
        return entity_to_response(entity) if entity else None


class ListAssetCategoriesUseCase:

    def __init__(self, repo: IAssetCategoryRepository):
        self._repo = repo

    def execute(
        self,
        tenant_id: int,
        search: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[AssetCategoryResponseDto], int]:
        entities, total = self._repo.list(
            tenant_id=tenant_id,
            search=search,
            limit=limit,
            offset=offset,
        )
        return [entity_to_response(e) for e in entities], total
