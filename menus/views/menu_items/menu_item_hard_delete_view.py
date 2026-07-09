from __future__ import annotations

import uuid

from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from menus.models import MenuItem
from menus.services.menu_item_service import MenuItemService


class MenuItemHardDeleteView(LoginRequiredMixin, View):
    """
    Handle MenuItem hard deletion.
    Django does not support direct HTTP DELETE from standard HTML forms,
    so we route POST request to delete method.
    """

    def post(self, request, pk: uuid.UUID):
        return self.delete(request, pk)

    def delete(self, request, pk: uuid.UUID):
        menu_item = get_object_or_404(MenuItem, uuid=pk)
        form = forms.Form(request.POST)
        if MenuItemService.hard_delete_menu_item(request, pk, form):
            messages.success(
                request, f"Menu item '{menu_item.label}' permanently deleted."
            )
        return redirect("menu_items_list")
