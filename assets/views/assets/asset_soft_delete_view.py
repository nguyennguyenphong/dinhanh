from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from assets.models import Asset
from assets.providers.asset_provider import AssetProvider


class AssetSoftDeleteView(LoginRequiredMixin, View):

    def post(self, request, pk: int):
        asset = get_object_or_404(Asset, id=pk)
        try:
            AssetProvider.delete_asset().execute(asset.id)
            messages.success(request, f"Đã xóa tạm thời tài sản '{asset.name}' thành công.")
        except Exception as exc:
            messages.error(request, f"Lỗi xóa tạm thời tài sản: {str(exc)}")

        return redirect("asset_list")
