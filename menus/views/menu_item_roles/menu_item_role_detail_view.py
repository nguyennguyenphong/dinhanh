from __future__ import annotations

import uuid

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from menus.services.menu_item_role_service import MenuItemRoleService


class MenuItemRoleDetailView(LoginRequiredMixin, View):
    """
    Handle viewing menu item role assignment details.
    """

    def get(self, request, pk: uuid.UUID):
        dto = MenuItemRoleService.get_by_uuid(pk)
        return render(
            request, "pages/menu_item_roles/detail.html", {"menu_item_role": dto}
        )
