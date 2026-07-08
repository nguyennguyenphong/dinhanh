from __future__ import annotations

import uuid

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from assets.models import StorageUnit
from assets.services.asset_service import AssetService
from assets.views.forms.storage_unit_base_form import StorageUnitBaseForm


class StorageUnitUpdateView(LoginRequiredMixin, View):

    def get(self, request, pk: uuid.UUID):
        storage_unit = get_object_or_404(StorageUnit, uuid=pk)
        form = StorageUnitBaseForm(instance=storage_unit)
        return render(
            request,
            "pages/storage_units/update.html",
            {"form": form, "object": storage_unit},
        )

    def post(self, request, pk: uuid.UUID):
        storage_unit = get_object_or_404(StorageUnit, uuid=pk)
        form = StorageUnitBaseForm(request.POST, instance=storage_unit)

        if form.is_valid():
            success = AssetService.update_storage_unit(request, pk, form)
            if success:
                return redirect("storage_unit_list")

        return render(
            request,
            "pages/storage_units/update.html",
            {"form": form, "object": storage_unit},
        )
