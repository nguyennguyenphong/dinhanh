from __future__ import annotations

import json

from django.contrib import messages
from django.shortcuts import get_object_or_404

from branches.application.dtos.branch_dtos import BranchCreateDto, BranchUpdateDto
from branches.models import Branch
from branches.providers.branch_provider import BranchProvider


class BranchService:

    @staticmethod
    def create_branch(request, form) -> bool:
        data = form.cleaned_data.copy()

        # Clean metadata JSON
        metadata = {}
        if data.get("metadata"):
            try:
                if isinstance(data.get("metadata"), str):
                    metadata = json.loads(data.get("metadata"))
                else:
                    metadata = data.get("metadata")
            except Exception:
                metadata = {}

        dto = BranchCreateDto(
            tenant_id=data.get("tenant").id if data.get("tenant") else 1,
            code=data.get("code"),
            name=data.get("name"),
            address=data.get("address"),
            phone=data.get("phone"),
            email=data.get("email"),
            manager_id=data.get("manager").id if data.get("manager") else None,
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            timezone=data.get("timezone") or "Asia/Ho_Chi_Minh",
            is_active=(
                data.get("is_active") if data.get("is_active") is not None else True
            ),
            metadata=metadata,
        )

        try:
            BranchProvider.create_branch().execute(dto)
            messages.success(request, "Tạo chi nhánh mới thành công.")
            return True
        except Exception as exc:
            form.add_error(None, str(exc))
            messages.error(request, f"Lỗi tạo chi nhánh: {str(exc)}")
            return False

    @staticmethod
    def update_branch(request, pk: int, form) -> bool:
        branch_model = get_object_or_404(Branch, id=pk)
        data = form.cleaned_data.copy()

        # Clean metadata JSON
        metadata = {}
        if data.get("metadata"):
            try:
                if isinstance(data.get("metadata"), str):
                    metadata = json.loads(data.get("metadata"))
                else:
                    metadata = data.get("metadata")
            except Exception:
                metadata = {}

        dto = BranchUpdateDto(
            id=branch_model.id,
            code=data.get("code"),
            name=data.get("name"),
            address=data.get("address"),
            phone=data.get("phone"),
            email=data.get("email"),
            manager_id=data.get("manager").id if data.get("manager") else None,
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            timezone=data.get("timezone") or "Asia/Ho_Chi_Minh",
            is_active=(
                data.get("is_active") if data.get("is_active") is not None else True
            ),
            metadata=metadata,
        )

        try:
            BranchProvider.update_branch().execute(dto)
            messages.success(request, "Cập nhật thông tin chi nhánh thành công.")
            return True
        except Exception as exc:
            form.add_error(None, str(exc))
            messages.error(request, f"Lỗi cập nhật chi nhánh: {str(exc)}")
            return False
