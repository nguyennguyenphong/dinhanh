from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from assets.models import StorageUnit
from assets.providers.asset_provider import AssetProvider


class StorageUnitHardDeleteView(LoginRequiredMixin, View):

    def post(self, request, pk: int):
        storage_unit = get_object_or_404(StorageUnit.all_objects, id=pk)
        try:
            AssetProvider.hard_delete_storage_unit().execute(storage_unit.id)
            messages.success(
                request, f"Đã xóa vĩnh viễn kho bãi '{storage_unit.name}' thành công."
            )
        except Exception as exc:
            messages.error(request, f"Lỗi xóa vĩnh viễn kho bãi: {str(exc)}")

        return redirect("storage_unit_list")
