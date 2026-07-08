from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from assets.services.asset_service import AssetService
from assets.views.forms.asset_base_form import AssetBaseForm


class AssetCreateView(LoginRequiredMixin, View):
    """
    Handle Asset creation.
    """

    def get(self, request):
        form = AssetBaseForm()
        return render(request, "pages/assets/create.html", {"form": form})

    def post(self, request):
        form = AssetBaseForm(request.POST)

        if form.is_valid():
            success = AssetService.create_asset(request, form)
            if success:
                return redirect("asset_list")

        return render(request, "pages/assets/create.html", {"form": form})
