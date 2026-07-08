from __future__ import annotations

import uuid
from decimal import Decimal

from django.contrib import messages
from django.shortcuts import get_object_or_404

from assets.application.dtos.asset_categories.asset_category_dtos import (
    AssetCategoryCreateDto,
    AssetCategoryUpdateDto,
)
from assets.application.dtos.assets.asset_dtos import AssetCreateDto, AssetUpdateDto
from assets.application.dtos.storage_units.storage_unit_dtos import (
    StorageUnitCreateDto,
    StorageUnitUpdateDto,
)
from assets.models import Asset, AssetCategory, StorageUnit
from assets.providers.asset_provider import AssetProvider


class AssetService:

    @staticmethod
    def create_asset(request, form) -> bool:
        """
        Processes form and calls UseCase. Adds errors to form if failed.
        """
        data = form.cleaned_data.copy()

        # Build Create DTO
        dto = AssetCreateDto(
            tenant_id=data.get("tenant").id if data.get("tenant") else 1,
            category_id=data.get("category").id if data.get("category") else None,
            branch_id=data.get("branch").id if data.get("branch") else None,
            assigned_to_id=(
                data.get("assigned_to").id if data.get("assigned_to") else None
            ),
            code=data.get("code"),
            name=data.get("name"),
            serial_number=data.get("serial_number"),
            purchase_date=data.get("purchase_date"),
            purchase_price=(
                Decimal(data.get("purchase_price"))
                if data.get("purchase_price") is not None
                else None
            ),
            depreciation_rate=(
                Decimal(data.get("depreciation_rate"))
                if data.get("depreciation_rate") is not None
                else None
            ),
            current_value=(
                Decimal(data.get("current_value"))
                if data.get("current_value") is not None
                else None
            ),
            warranty_expiry=data.get("warranty_expiry"),
            status=data.get("status"),
            notes=data.get("notes"),
        )

        try:
            AssetProvider.create_asset().execute(dto)
            messages.success(request, "Tạo tài sản mới thành công.")
            return True
        except Exception as exc:
            form.add_error(None, str(exc))
            messages.error(request, f"Lỗi tạo tài sản: {str(exc)}")
            return False

    @staticmethod
    def update_asset(request, pk: uuid.UUID, form) -> bool:
        """
        Processes form and calls UseCase. Adds errors to form if failed.
        """
        asset_model = get_object_or_404(Asset, uuid=pk)
        data = form.cleaned_data.copy()

        # Build Update DTO
        dto = AssetUpdateDto(
            id=asset_model.id,
            category_id=data.get("category").id if data.get("category") else None,
            branch_id=data.get("branch").id if data.get("branch") else None,
            assigned_to_id=(
                data.get("assigned_to").id if data.get("assigned_to") else None
            ),
            code=data.get("code"),
            name=data.get("name"),
            serial_number=data.get("serial_number"),
            purchase_date=data.get("purchase_date"),
            purchase_price=(
                Decimal(data.get("purchase_price"))
                if data.get("purchase_price") is not None
                else None
            ),
            depreciation_rate=(
                Decimal(data.get("depreciation_rate"))
                if data.get("depreciation_rate") is not None
                else None
            ),
            current_value=(
                Decimal(data.get("current_value"))
                if data.get("current_value") is not None
                else None
            ),
            warranty_expiry=data.get("warranty_expiry"),
            status=data.get("status"),
            notes=data.get("notes"),
        )

        try:
            AssetProvider.update_asset().execute(dto)
            messages.success(request, "Cập nhật tài sản thành công.")
            return True
        except Exception as exc:
            form.add_error(None, str(exc))
            messages.error(request, f"Lỗi cập nhật tài sản: {str(exc)}")
            return False

    @staticmethod
    def create_category(request, form) -> bool:
        data = form.cleaned_data.copy()
        dto = AssetCategoryCreateDto(
            tenant_id=data.get("tenant").id if data.get("tenant") else 1,
            name=data.get("name"),
        )
        try:
            AssetProvider.create_category().execute(dto)
            messages.success(request, "Tạo danh mục tài sản mới thành công.")
            return True
        except Exception as exc:
            form.add_error(None, str(exc))
            messages.error(request, f"Lỗi tạo danh mục tài sản: {str(exc)}")
            return False

    @staticmethod
    def update_category(request, pk: uuid.UUID, form) -> bool:
        category_model = get_object_or_404(AssetCategory, uuid=pk)
        data = form.cleaned_data.copy()
        dto = AssetCategoryUpdateDto(
            id=category_model.id,
            name=data.get("name"),
        )
        try:
            AssetProvider.update_category().execute(dto)
            messages.success(request, "Cập nhật danh mục tài sản thành công.")
            return True
        except Exception as exc:
            form.add_error(None, str(exc))
            messages.error(request, f"Lỗi cập nhật danh mục tài sản: {str(exc)}")
            return False

    @staticmethod
    def create_storage_unit(request, form) -> bool:
        data = form.cleaned_data.copy()
        dto = StorageUnitCreateDto(
            tenant_id=data.get("tenant").id if data.get("tenant") else 1,
            branch_id=data.get("branch").id if data.get("branch") else None,
            code=data.get("code"),
            name=data.get("name"),
            description=data.get("description"),
        )
        try:
            AssetProvider.create_storage_unit().execute(dto)
            messages.success(request, "Tạo kho bãi mới thành công.")
            return True
        except Exception as exc:
            form.add_error(None, str(exc))
            messages.error(request, f"Lỗi tạo kho bãi: {str(exc)}")
            return False

    @staticmethod
    def update_storage_unit(request, pk: uuid.UUID, form) -> bool:
        storage_model = get_object_or_404(StorageUnit, uuid=pk)
        data = form.cleaned_data.copy()
        dto = StorageUnitUpdateDto(
            id=storage_model.id,
            branch_id=data.get("branch").id if data.get("branch") else None,
            code=data.get("code"),
            name=data.get("name"),
            description=data.get("description"),
        )
        try:
            AssetProvider.update_storage_unit().execute(dto)
            messages.success(request, "Cập nhật kho bãi thành công.")
            return True
        except Exception as exc:
            form.add_error(None, str(exc))
            messages.error(request, f"Lỗi cập nhật kho bãi: {str(exc)}")
            return False
