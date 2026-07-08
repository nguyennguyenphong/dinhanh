from __future__ import annotations

import uuid
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views import View

from assets.models import Asset
from assets.providers.asset_provider import AssetProvider


class AssetDetailView(LoginRequiredMixin, View):
    """
    Handle viewing an asset in MVT style.
    """

    def get(self, request, pk: uuid.UUID):
        asset = get_object_or_404(Asset, uuid=pk)
        asset_dto = AssetProvider.get_asset().execute_by_uuid(str(pk))
        return render(
            request,
            "pages/assets/detail.html",
            {"asset": asset_dto, "object": asset},
        )
