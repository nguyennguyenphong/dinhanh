from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from assets.views.forms import AssetCategoryBaseForm


class AssetCategoryUpdateView(LoginRequiredMixin, View):
    def get(self, request):
        form = AssetCategoryBaseForm()
        return render(request, "pages/asset_categories/update.html", {"form": form})
