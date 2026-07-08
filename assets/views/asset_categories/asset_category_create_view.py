from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from assets.services.asset_service import AssetService
from assets.views.forms.asset_category_base_form import AssetCategoryBaseForm


class AssetCategoryCreateView(LoginRequiredMixin, View):

    def get(self, request):
        form = AssetCategoryBaseForm()
        return render(request, "pages/asset_categories/create.html", {"form": form})

    def post(self, request):
        form = AssetCategoryBaseForm(request.POST)

        if form.is_valid():
            success = AssetService.create_category(request, form)
            if success:
                return redirect("asset_category_list")

        return render(request, "pages/asset_categories/create.html", {"form": form})
