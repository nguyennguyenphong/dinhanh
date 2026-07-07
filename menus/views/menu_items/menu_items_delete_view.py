from __future__ import annotations

import uuid

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import Form
from django.shortcuts import redirect
from django.views import View

from menus.services.menu_item_service import MenuItemService


class MenuItemDeleteView(LoginRequiredMixin, View):
    """
    Handle MenuItem deletion (soft delete).
    """

    def post(self, request, pk: uuid.UUID):
        form = Form(request.POST)
        success = MenuItemService.delete_menu_item(request, pk, form)
        if success:
            messages.success(request, "Menu item deleted successfully.")
        return redirect("menu_items_list")
