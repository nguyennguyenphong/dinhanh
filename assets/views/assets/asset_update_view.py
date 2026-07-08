from __future__ import annotations

import uuid
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from assets.models import Asset
from assets.services.asset_service import AssetService
from assets.views.forms.asset_base_form import AssetBaseForm


class AssetUpdateView(LoginRequiredMixin, View):
    """
    Handle Asset updates.
    """

    def get(self, request, pk: uuid.UUID):
        asset = get_object_or_404(Asset, uuid=pk)
        form = AssetBaseForm(instance=asset)
        return render(
            request,
            "pages/assets/update.html",
            {"form": form, "object": asset},
        )

    def post(self, request, pk: uuid.UUID):
        asset = get_object_or_404(Asset, uuid=pk)
        form = AssetBaseForm(request.POST, instance=asset)

        if form.is_valid():
            success = AssetService.update_asset(request, pk, form)
            if success:
                return redirect("asset_list")

        return render(
            request,
            "pages/assets/update.html",
            {"form": form, "object": asset},
        )
