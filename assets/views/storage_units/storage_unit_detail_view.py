from __future__ import annotations

import uuid

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views import View

from assets.models import StorageUnit
from assets.providers.asset_provider import AssetProvider


class StorageUnitDetailView(LoginRequiredMixin, View):

    def get(self, request, pk: int):
        storage_unit = get_object_or_404(StorageUnit, id=pk)
        storage_dto = AssetProvider.get_storage_unit().execute(storage_unit.id)
        return render(
            request,
            "pages/storage_units/detail.html",
            {"storage_unit": storage_dto, "object": storage_unit},
        )
