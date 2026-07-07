from __future__ import annotations

import uuid

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import Form
from django.shortcuts import redirect
from django.views import View

from menus.services.menu_item_role_service import MenuItemRoleService


class MenuItemRoleSoftDeleteView(LoginRequiredMixin, View):
    """
    Handle MenuItemRole assignment soft deletion.
    """

    def post(self, request, pk: uuid.UUID):
        form = Form(request.POST)
        success = MenuItemRoleService.delete_menu_item_role(request, pk, form)
        if success:
            messages.success(request, "Role assignment soft deleted.")
        return redirect("menu_item_role_list")


class MenuItemRoleHardDeleteView(LoginRequiredMixin, View):
    """
    Handle MenuItemRole assignment hard deletion.
    """

    def post(self, request, pk: uuid.UUID):
        form = Form(request.POST)
        success = MenuItemRoleService.hard_delete_menu_item_role(request, pk, form)
        if success:
            messages.success(request, "Role assignment permanently deleted.")
        return redirect("menu_item_role_list")
