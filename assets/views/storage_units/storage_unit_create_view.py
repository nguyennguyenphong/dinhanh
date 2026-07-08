from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from assets.services.asset_service import AssetService
from assets.views.forms.storage_unit_base_form import StorageUnitBaseForm


class StorageUnitCreateView(LoginRequiredMixin, View):

    def get(self, request):
        form = StorageUnitBaseForm()
        return render(request, "pages/storage_units/create.html", {"form": form})

    def post(self, request):
        form = StorageUnitBaseForm(request.POST)

        if form.is_valid():
            success = AssetService.create_storage_unit(request, form)
            if success:
                return redirect("storage_unit_list")

        return render(request, "pages/storage_units/create.html", {"form": form})
