from __future__ import annotations

import uuid

from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View

from menus.services.menu_item_role_service import MenuItemRoleService


class MenuItemRoleSoftDeleteView(LoginRequiredMixin, View):
    """
    Handle MenuItemRole soft deletion.
    Django does not support direct HTTP DELETE from standard HTML forms,
    so we route POST request to delete method.
    """

    def post(self, request, pk: uuid.UUID):
        return self.delete(request, pk)

    def delete(self, request, pk: uuid.UUID):
        form = forms.Form(request.POST)
        if MenuItemRoleService.delete_menu_item_role(request, pk, form):
            messages.success(request, "Role assignment soft deleted.")
        return redirect("menu_item_role_list")
