from __future__ import annotations

from assets.application.usecases.assets.create_asset_usecase import CreateAssetUseCase
from assets.application.usecases.assets.delete_asset_usecase import DeleteAssetUseCase
from assets.application.usecases.assets.get_asset_detail_usecase import GetAssetDetailUseCase
from assets.application.usecases.assets.list_assets_usecase import ListAssetsUseCase
from assets.application.usecases.assets.update_asset_usecase import UpdateAssetUseCase
from assets.application.usecases.asset_categories.asset_category_usecases import (
    CreateAssetCategoryUseCase,
    UpdateAssetCategoryUseCase,
    DeleteAssetCategoryUseCase,
    GetAssetCategoryDetailUseCase,
    ListAssetCategoriesUseCase,
)
from assets.application.usecases.storage_units.storage_unit_usecases import (
    CreateStorageUnitUseCase,
    UpdateStorageUnitUseCase,
    DeleteStorageUnitUseCase,
    GetStorageUnitDetailUseCase,
    ListStorageUnitsUseCase,
)
from assets.repositories.implement.asset_category_repository_impl import AssetCategoryRepositoryImpl
from assets.repositories.implement.asset_repository_impl import AssetRepositoryImpl
from assets.repositories.implement.storage_unit_repository_impl import StorageUnitRepositoryImpl


class AssetProvider:

    @staticmethod
    def asset_repo() -> AssetRepositoryImpl:
        return AssetRepositoryImpl()

    @staticmethod
    def category_repo() -> AssetCategoryRepositoryImpl:
        return AssetCategoryRepositoryImpl()

    @staticmethod
    def storage_unit_repo() -> StorageUnitRepositoryImpl:
        return StorageUnitRepositoryImpl()

    @classmethod
    def create_asset(cls) -> CreateAssetUseCase:
        return CreateAssetUseCase(cls.asset_repo())

    @classmethod
    def update_asset(cls) -> UpdateAssetUseCase:
        return UpdateAssetUseCase(cls.asset_repo())

    @classmethod
    def delete_asset(cls) -> DeleteAssetUseCase:
        return DeleteAssetUseCase(cls.asset_repo())

    @classmethod
    def get_asset(cls) -> GetAssetDetailUseCase:
        return GetAssetDetailUseCase(cls.asset_repo())

    @classmethod
    def list_assets(cls) -> ListAssetsUseCase:
        return ListAssetsUseCase(cls.asset_repo())

    # AssetCategory Use Cases
    @classmethod
    def create_category(cls) -> CreateAssetCategoryUseCase:
        return CreateAssetCategoryUseCase(cls.category_repo())

    @classmethod
    def update_category(cls) -> UpdateAssetCategoryUseCase:
        return UpdateAssetCategoryUseCase(cls.category_repo())

    @classmethod
    def delete_category(cls) -> DeleteAssetCategoryUseCase:
        return DeleteAssetCategoryUseCase(cls.category_repo())

    @classmethod
    def get_category(cls) -> GetAssetCategoryDetailUseCase:
        return GetAssetCategoryDetailUseCase(cls.category_repo())

    @classmethod
    def list_categories(cls) -> ListAssetCategoriesUseCase:
        return ListAssetCategoriesUseCase(cls.category_repo())

    # StorageUnit Use Cases
    @classmethod
    def create_storage_unit(cls) -> CreateStorageUnitUseCase:
        return CreateStorageUnitUseCase(cls.storage_unit_repo())

    @classmethod
    def update_storage_unit(cls) -> UpdateStorageUnitUseCase:
        return UpdateStorageUnitUseCase(cls.storage_unit_repo())

    @classmethod
    def delete_storage_unit(cls) -> DeleteStorageUnitUseCase:
        return DeleteStorageUnitUseCase(cls.storage_unit_repo())

    @classmethod
    def get_storage_unit(cls) -> GetStorageUnitDetailUseCase:
        return GetStorageUnitDetailUseCase(cls.storage_unit_repo())

    @classmethod
    def list_storage_units(cls) -> ListStorageUnitsUseCase:
        return ListStorageUnitsUseCase(cls.storage_unit_repo())
