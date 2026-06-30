from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from assets.views.forms import AssetCategoryBaseForm


class AssetCategoryCreateView(LoginRequiredMixin, View):
    """
    Handle Menu creation:
    1. GET: Render the creation form.
    2. POST: Validate data, process file upload, execute UseCase, and redirect.
    """

    def get(self, request):
        form = AssetCategoryBaseForm()
        return render(request, "pages/asset_categories/create.html", {"form": form})
