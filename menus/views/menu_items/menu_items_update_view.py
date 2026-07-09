from __future__ import annotations

import uuid

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from menus.models.menu_items import MenuItem
from menus.services.menu_item_service import MenuItemService
from menus.views.forms.menu_item_base_form import MenuItemBaseForm


class MenuItemUpdateView(LoginRequiredMixin, View):
    """
    Handle MenuItem update:
    1. GET: Render the edit form populated with current values.
    2. POST: Map POST to PATCH.
    3. PATCH: Validate data, execute UseCase, and redirect.
    """

    def get(self, request, pk: uuid.UUID):
        menu_item = get_object_or_404(MenuItem, uuid=pk)
        form = MenuItemBaseForm(instance=menu_item)
        return render(
            request,
            "pages/menu_items/update.html",
            {"form": form, "menu_item": menu_item},
        )

    def post(self, request, pk: uuid.UUID):
        return self.patch(request, pk)

    def patch(self, request, pk: uuid.UUID):
        menu_item = get_object_or_404(MenuItem, uuid=pk)
        form = MenuItemBaseForm(request.POST, instance=menu_item)

        if form.is_valid():
            success = MenuItemService.update_menu_item(request, pk, form)

            if success:
                messages.success(request, "Menu item updated successfully.")
                return redirect("menu_items_list")

        return render(
            request,
            "pages/menu_items/update.html",
            {"form": form, "menu_item": menu_item},
        )
