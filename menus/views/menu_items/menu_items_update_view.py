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
    2. POST: Validate data, execute UseCase, and redirect.
    """

    def get(self, request, pk: uuid.UUID):
        menu_item = get_object_or_404(MenuItem, uuid=pk)

        initial_data = {
            "tenant": menu_item.tenant_id,
            "code": menu_item.code,
            "label": menu_item.label,
            "group": menu_item.group_id,
            "parent": menu_item.parent_id,
            "url_name": menu_item.url_name,
            "url_path": menu_item.url_path,
            "icon": menu_item.icon,
            "badge": menu_item.badge_text,
            "permission_code": menu_item.permission_code,
            "sort_order": menu_item.sort_order,
            "open_in_new_tab": menu_item.open_in_new_tab,
            "is_active": menu_item.is_active,
            "is_hidden": menu_item.is_hidden,
        }
        form = MenuItemBaseForm(initial=initial_data)
        return render(
            request,
            "pages/menu_items/update.html",
            {"form": form, "menu_item": menu_item},
        )

    def post(self, request, pk: uuid.UUID):
        menu_item = get_object_or_404(MenuItem, uuid=pk)
        form = MenuItemBaseForm(request.POST)

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
