"""
DRF API views for Menu CRUD operations.

Endpoint map (wired in urls/menu_urls.py):
    POST   /menus/                -> MenuItemView
"""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from assets.views.forms import AssetBaseForm


class AssetUpdateView(LoginRequiredMixin, View):
    """
    Handle Menu creation:
    1. GET: Render the creation form.
    2. POST: Validate data, process file upload, execute UseCase, and redirect.
    """

    def get(self, request):
        form = AssetBaseForm()
        return render(request, "pages/assets/update.html", {"form": form})
