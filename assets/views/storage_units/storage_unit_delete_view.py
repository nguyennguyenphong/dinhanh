from __future__ import annotations

import uuid

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from assets.models import StorageUnit
from assets.providers.asset_provider import AssetProvider


class StorageUnitDeleteView(LoginRequiredMixin, View):

    def post(self, request, pk: uuid.UUID):
        storage_unit = get_object_or_404(StorageUnit, uuid=pk)
        try:
            AssetProvider.delete_storage_unit().execute(storage_unit.id)
            messages.success(
                request, f"Đã xóa kho bãi '{storage_unit.name}' thành công."
            )
        except Exception as exc:
            messages.error(request, f"Lỗi xóa kho bãi: {str(exc)}")

        return redirect("storage_unit_list")
