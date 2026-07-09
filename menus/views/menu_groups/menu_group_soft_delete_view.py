from __future__ import annotations

import uuid

from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View

from menus.services import MenuGroupService


class MenuGroupSoftDeleteView(LoginRequiredMixin, View):
    """
    Handle MenuGroup soft deletion.
    Django does not support direct HTTP DELETE from standard HTML forms,
    so we route POST request to delete method.
    """

    def post(self, request, pk: uuid.UUID):
        return self.delete(request, pk)

    def delete(self, request, pk: uuid.UUID):
        form = forms.Form(request.POST)
        if MenuGroupService.soft_delete_menu_group(request, pk, form):
            messages.success(request, "Menu group deleted successfully.")
        return redirect("menu_group_list")
