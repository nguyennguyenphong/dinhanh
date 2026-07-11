from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from assets.models import AssetCategory
from assets.providers.asset_provider import AssetProvider


class AssetCategoryHardDeleteView(LoginRequiredMixin, View):

    def post(self, request, pk: int):
        category = get_object_or_404(AssetCategory.all_objects, id=pk)
        try:
            AssetProvider.hard_delete_category().execute(category.id)
            messages.success(
                request,
                f"Đã xóa vĩnh viễn danh mục tài sản '{category.name}' thành công.",
            )
        except Exception as exc:
            messages.error(request, f"Lỗi xóa vĩnh viễn danh mục tài sản: {str(exc)}")

        return redirect("asset_category_list")
