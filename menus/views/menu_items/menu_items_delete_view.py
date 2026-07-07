from __future__ import annotations

import uuid

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import Form
from django.shortcuts import redirect
from django.views import View

from menus.services.menu_item_service import MenuItemService


class MenuItemSoftDeleteView(LoginRequiredMixin, View):
    """
    Handle MenuItem soft deletion.
    """

    def post(self, request, pk: uuid.UUID):
        form = Form(request.POST)
        success = MenuItemService.delete_menu_item(request, pk, form)
        if success:
            messages.success(request, "Menu item deleted successfully.")
        return redirect("menu_items_list")


class MenuItemHardDeleteView(LoginRequiredMixin, View):
    """
    Handle MenuItem hard deletion.
    """

    def post(self, request, pk: uuid.UUID):
        form = Form(request.POST)
        success = MenuItemService.hard_delete_menu_item(request, pk, form)
        if success:
            messages.success(request, "Menu item permanently deleted.")
        return redirect("menu_items_list")


# Backwards compatibility alias
MenuItemDeleteView = MenuItemSoftDeleteView
