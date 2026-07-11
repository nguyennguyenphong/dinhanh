from __future__ import annotations

import uuid

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views import View

from assets.models import AssetCategory
from assets.providers.asset_provider import AssetProvider


class AssetCategoryDetailView(LoginRequiredMixin, View):

    def get(self, request, pk: int):
        category = get_object_or_404(AssetCategory, id=pk)
        category_dto = AssetProvider.get_category().execute(category.id)
        return render(
            request,
            "pages/asset_categories/detail.html",
            {"category": category_dto, "object": category},
        )
