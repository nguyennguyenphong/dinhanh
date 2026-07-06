"""
DRF API views for Menu CRUD operations.

Endpoint map (wired in urls/menu_urls.py):
    POST   /menus/                -> MenuItemView
"""

from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from menus.views.forms import MenuGroupBaseForm


class MenuItemRoleUpdateView(LoginRequiredMixin, View):
    """
    Handle Menu creation:
    1. GET: Render the creation form.
    2. POST: Validate data, process file upload, execute UseCase, and redirect.
    """

    def get(self, request):
        form = MenuGroupBaseForm()
        return render(request, "pages/menu_item_roles/update.html", {"form": form})
