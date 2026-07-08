from __future__ import annotations

import uuid
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from assets.models import Asset
from assets.providers.asset_provider import AssetProvider


class AssetDeleteView(LoginRequiredMixin, View):
    """
    Handle permanent Asset deletion.
    """

    def post(self, request, pk: uuid.UUID):
        asset = get_object_or_404(Asset, uuid=pk)
        try:
            AssetProvider.delete_asset().execute(asset.id)
            messages.success(request, f"Đã xóa tài sản '{asset.name}' thành công.")
        except Exception as exc:
            messages.error(request, f"Lỗi xóa tài sản: {str(exc)}")

        return redirect("asset_list")
