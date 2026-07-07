from __future__ import annotations

import uuid

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from menus.services.menu_item_service import MenuItemService


class MenuItemDetailView(LoginRequiredMixin, View):
    """
    Handle viewing menu item details in MVT style.
    """

    def get(self, request, pk: uuid.UUID):
        menu_item_dto = MenuItemService.get_by_uuid(pk)
        return render(
            request, "pages/menu_items/detail.html", {"menu_item": menu_item_dto}
        )
