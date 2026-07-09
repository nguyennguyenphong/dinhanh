from __future__ import annotations

import uuid

from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from menus.models import MenuGroup
from menus.services import MenuGroupService


class MenuGroupHardDeleteView(LoginRequiredMixin, View):
    """
    Handle MenuGroup hard deletion.
    Django does not support direct HTTP DELETE from standard HTML forms,
    so we route POST request to delete method.
    """

    def post(self, request, pk: uuid.UUID):
        return self.delete(request, pk)

    def delete(self, request, pk: uuid.UUID):
        menu_group = get_object_or_404(MenuGroup, uuid=pk)
        form = forms.Form(request.POST)
        if MenuGroupService.hard_delete_menu_group(request, pk, form):
            messages.success(
                request, f"Menu group '{menu_group.label}' permanently deleted."
            )
        return redirect("menu_group_list")
