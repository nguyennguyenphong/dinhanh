from __future__ import annotations

import uuid

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from assets.models import AssetCategory
from assets.providers.asset_provider import AssetProvider


class AssetCategoryDeleteView(LoginRequiredMixin, View):

    def post(self, request, pk: uuid.UUID):
        category = get_object_or_404(AssetCategory, uuid=pk)
        try:
            AssetProvider.delete_category().execute(category.id)
            messages.success(
                request, f"Đã xóa danh mục tài sản '{category.name}' thành công."
            )
        except Exception as exc:
            messages.error(request, f"Lỗi xóa danh mục tài sản: {str(exc)}")

        return redirect("asset_category_list")
