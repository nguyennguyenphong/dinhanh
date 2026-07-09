from __future__ import annotations

import uuid

from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from menus.models import MenuItemRole
from menus.services.menu_item_role_service import MenuItemRoleService


class MenuItemRoleHardDeleteView(LoginRequiredMixin, View):
    """
    Handle MenuItemRole hard deletion.
    Django does not support direct HTTP DELETE from standard HTML forms,
    so we route POST request to delete method.
    """

    def post(self, request, pk: uuid.UUID):
        return self.delete(request, pk)

    def delete(self, request, pk: uuid.UUID):
        menu_item_role = get_object_or_404(MenuItemRole, uuid=pk)
        form = forms.Form(request.POST)
        if MenuItemRoleService.hard_delete_menu_item_role(request, pk, form):
            messages.success(
                request, f"Role assignment '{menu_item_role.uuid}' permanently deleted."
            )
        return redirect("menu_item_role_list")
