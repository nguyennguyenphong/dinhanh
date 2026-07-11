from __future__ import annotations

import uuid

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from assets.models import AssetCategory
from assets.services.asset_service import AssetService
from assets.views.forms.asset_category_base_form import AssetCategoryBaseForm


class AssetCategoryUpdateView(LoginRequiredMixin, View):

    def get(self, request, pk: int):
        category = get_object_or_404(AssetCategory, id=pk)
        form = AssetCategoryBaseForm(instance=category)
        return render(
            request,
            "pages/asset_categories/update.html",
            {"form": form, "object": category},
        )

    def post(self, request, pk: int):
        category = get_object_or_404(AssetCategory, id=pk)
        form = AssetCategoryBaseForm(request.POST, instance=category)

        if form.is_valid():
            success = AssetService.update_category(request, pk, form)
            if success:
                return redirect("asset_category_list")

        return render(
            request,
            "pages/asset_categories/update.html",
            {"form": form, "object": category},
        )
